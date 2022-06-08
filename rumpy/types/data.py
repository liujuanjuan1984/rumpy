import base64
import dataclasses
import json
import logging
import os
import time
import uuid
from typing import Any, Dict, List

import filetype

logger = logging.getLogger(__name__)

TRX_TYPES = [
    "POST",
    "ANNOUNCE",
    "REQ_BLOCK_FORWARD",
    "REQ_BLOCK_BACKWARD",
    "BLOCK_SYNCED",
    "BLOCK_PRODUCED",
    "ASK_PEERID",
]

API_PAYMENT_GATEWAY: str = "https://prs-bp2.press.one/api"
IMAGE_MAX_SIZE_KB = 200  # kb 每条trx中所包含的图片总大小限制为 200
CHUNK_SIZE = 150 * 1024  # 150kb


@dataclasses.dataclass
class ApiBaseURLS:
    FULL_NODE: str
    LIGHT_NODE: str
    PAYMENT_GATEWAY = API_PAYMENT_GATEWAY

    def __init__(self, port=None, host="127.0.0.1"):
        self.FULL_NODE = f"https://{host}:{port}"
        self.LIGHT_NODE = f"https://{host}:{port}/nodesdk_api"


@dataclasses.dataclass
class NodeInfo:
    node_id: str
    node_publickey: str
    node_status: str
    node_type: str
    node_version: str
    peers: Dict

    def values(self):
        """供 sql 调用"""
        return (
            self.node_id,
            self.node_publickey,
            self.node_status,
            self.node_type,
            self.node_version,
            json.dumps(self.peers),
        )


@dataclasses.dataclass
class Block:
    BlockId: str
    GroupId: str
    ProducerPubKey: str
    Hash: str
    Signature: str
    TimeStamp: str


@dataclasses.dataclass
class Seed:
    genesis_block: Block.__dict__
    group_id: str
    group_name: str
    consensus_type: str
    encryption_type: str
    cipher_key: str
    app_key: str
    signature: str
    owner_pubkey: str
    owner_encryptpubkey: str = None  # 新版本似乎弃用该字段了


def is_seed(seed: Dict) -> bool:
    try:
        Seed(**seed)
        return True
    except Exception as e:
        logger.error(f"{e}")
        return False


@dataclasses.dataclass
class SnapShotInfo:
    TimeStamp: int
    HighestHeight: int
    HighestBlockId: str
    Nonce: int
    SnapshotPackageId: str
    SenderPubkey: str


@dataclasses.dataclass
class GroupInfo:
    group_id: str
    group_name: str
    owner_pubkey: str
    user_pubkey: str
    user_eth_addr: str
    consensus_type: str
    encryption_type: str
    cipher_key: str
    app_key: str
    last_updated: int
    highest_height: int
    highest_block_id: str
    group_status: str
    snapshot_info: SnapShotInfo.__dict__


@dataclasses.dataclass
class ProfileParams:
    name: str = None
    image: str = None
    wallet: str = None

    def __post_init__(self):
        d = {}
        if self.name:
            d["name"] = self.name

        if self.image:
            d["image"] = {"mediaType": "image/png", "content": self.image}

        if self.wallet:
            d["wallet"] = [{"id": self.wallet, "type": "mixin", "name": "mixin messenger"}]

        if len(d) == 0:
            raise ValueError("Person must have name or image fields")
        self.__dict__ = d


@dataclasses.dataclass
class NewTrxImg:
    """将一张图片处理成 RUM 支持的图片对象, 例如用户头像, 要求大小小于 200kb

    kb: 设置图片大小, 需要小于 200kb
    """

    def __init__(self, file_path=None, file_bytes=None, kb=None):

        from rumpy.utils import zip_image_file

        kb = kb or IMAGE_MAX_SIZE_KB

        if file_path == None and file_bytes == None:
            raise ValueError("need file_path or file_bytes")

        if file_path:
            file_bytes = zip_image_file(file_path, kb)
            self.name = os.path.basename(file_path).encode().decode("utf-8")

        if file_bytes:
            extension = filetype.guess(file_bytes).extension
            name = f"{uuid.uuid4()}-{round(int(time.time()*1000000))}"
            self.name = ".".join([name, extension])

        self.mediaType = filetype.guess(file_bytes).mime
        self.content = base64.b64encode(file_bytes).decode("utf-8")


@dataclasses.dataclass
class NewTrxObject:
    def __init__(
        self,
        object_type: str = None,
        content: str = None,
        name: str = None,
        images: List = None,
        edit_trx_id: str = None,
        del_trx_id: str = None,
        like_trx_id: str = None,
        reply_trx_id: str = None,  # inreplyto
    ):
        """the object of activity (NewTrx params)

        Args:
            object_type (str, optional): one of Note,File,and None (with activity_type: Like or Dislike). Defaults to None.
            edit_trx_id (str, optional): trx_id to edit or delete (just client show it). Defaults to None.
            like_trx_id (str, optional): like or dislike to trx_id. Defaults to None.
            images (List, optional): list of NewTrxImg . Defaults to None.
            name (str, optional): used as title in bbs post. Defaults to None.
            reply_trx_id(str, optional): trx_id to reply. Defaults to None.
        """
        if object_type in ["Note", "File"]:
            self.type = object_type
        elif object_type:
            raise ValueError(f"new object_type: {object_type}. check the param or update rumpy code.")

        if content:
            if type(content) == str:
                self.content = content
            elif type(content) in (dict, list):
                self.content = json.dumps(content)
            else:
                raise ValueError(f"new content type: {type(content)}. check the param or update rumpy code.")

        if name and type(name) == str:
            self.name = name

        if images:  # 待优化 TODO
            # 将一张或多张图片处理成 RUM 支持的图片对象列表, 要求总大小小于 200kb
            # 客户端限定：单条 trx 最多4 张图片
            kb = int(200 // min(len(images), 4))
            self.image = [NewTrxImg(file_path=file_path, kb=kb).__dict__ for file_path in images[:4]]

        if edit_trx_id and type(edit_trx_id) == str:
            self.id = edit_trx_id
            # check other params:
            if self.type != "Note":
                raise ValueError(f"only Note type can be edited. type now: {self.type} ")
            if not (self.content or self.images):
                raise ValueError("content or images is needed.")

        if del_trx_id and type(del_trx_id) == str:
            self.id = del_trx_id
            # check other params
            self.content = "OBJECT_STATUS_DELETED"
            for key in self.__dict__:
                if key not in ["type", "id", "content"]:
                    raise ValueError(f"del object got a no-need param {key}")

        if reply_trx_id and type(reply_trx_id) == str:
            self.inreplyto = {"trxid": reply_trx_id}
            if not (self.content or self.images):
                raise ValueError("content or images is needed.")

        if like_trx_id and type(like_trx_id) == str:
            self.id = like_trx_id
            # check other params: only id param is needed.
            for key in self.__dict__:
                if key != "id":
                    raise ValueError(f"like or dislike object can only have id param. but param {key} is found.")


@dataclasses.dataclass
class FileObj(NewTrxObject):
    def __init__(self, content: bytes, name: str, mediaType: str):
        self.type = "File"
        self.name = name
        self.file = {
            "compression": 0,
            "mediaType": mediaType,
            "content": base64.b64encode(content).decode("utf-8"),
        }


@dataclasses.dataclass
class NewTrx:
    def __init__(self, activity_type, group_id, obj=None, **kwargs):
        self.type = activity_type
        if self.type not in [4, "Add", "Like", "Dislike"]:
            raise ValueError(
                f"{self.type} is not one of 4,Add,Like,Dislike... check the input params or update the rumpy code. "
            )

        if group_id:
            self.target = {"id": group_id, "type": "Group"}
        else:
            raise ValueError("group_id param is need.")

        if isinstance(obj, NewTrxObject):
            self.object = NewTrxObject(**obj.__dict__).__dict__
        elif isinstance(obj, dict):
            if self.type == "Add" and "type" not in obj:
                raise ValueError("obj need a `type` such as: `Note` or `File`")
            self.object = NewTrxObject(**obj).__dict__
        else:
            self.object = NewTrxObject(**kwargs).__dict__
