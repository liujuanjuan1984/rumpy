import base64
import dataclasses
import json
import logging
import os
import time
from typing import Any, Dict, List

import filetype

from rumpy.exceptions import *

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
# 将一张或多张图片处理成 RUM 支持的图片对象列表, 要求总大小小于 200kb，此为链端限定
IMAGE_MAX_SIZE_KB = 200  # 200 kb 每条trx中所包含的图片总大小限制为 200
# 单条 trx 最多4 张图片；此为 rum app 客户端限定：第三方 app 调整该限定
IMAGE_MAX_NUM = 4
CHUNK_SIZE = 150 * 1024  # 150 kb，文件切割为多条trxs时，每条trx所包含的文件字节流上限


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
            raise ParamRequiredError("Person must have name or image fields")
        self.__dict__ = d


@dataclasses.dataclass
class NewTrxImg:
    def __init__(self, path_bytes_string, kb=None):
        from rumpy.utils import filename_init, get_filebytes, zip_image

        if type(path_bytes_string) == dict:
            d = path_bytes_string
            self.content = d.get("content")
            if not self.content:
                raise ParamValueError(
                    403,
                    f"NewTrxImg  type: {type(path_bytes_string)} ,content got null ",
                )
            _bytes, _ = get_filebytes(self.content)
            self.name = d.get("name", filename_init(_bytes))
            self.mediaType = d.get("mediaType", filetype.guess(_bytes).mime)

        else:
            kb = kb or IMAGE_MAX_SIZE_KB
            self.name = filename_init(path_bytes_string)
            file_bytes = zip_image(path_bytes_string, kb)
            self.mediaType = filetype.guess(file_bytes).mime
            self.content = base64.b64encode(file_bytes).decode("utf-8")

    def person_img(self):
        return {"content": self.content, "mediaType": self.mediaType}


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
            raise ParamTypeError(
                403,
                f"new object_type: {object_type}. check the param or update rumpy code.",
            )

        if content:
            if type(content) == str:
                self.content = content
            elif type(content) in (dict, list):
                self.content = json.dumps(content)
            else:
                raise ParamTypeError(
                    403,
                    f"new content type: {type(content)}. check the param or update rumpy code.",
                )

        if name and type(name) == str:
            self.name = name

        if images:
            kb = int(IMAGE_MAX_SIZE_KB // min(len(images), IMAGE_MAX_NUM))
            self.image = [NewTrxImg(i, kb=kb).__dict__ for i in images[:IMAGE_MAX_NUM]]

        if edit_trx_id and type(edit_trx_id) == str:
            self.id = edit_trx_id
            # check other params:
            if self.type != "Note":
                raise ParamOverflowError(f"only Note type can be edited. type now: {self.type} ")
            if not (self.content or self.image):
                raise ParamRequiredError("content or image is needed.")

        if del_trx_id and type(del_trx_id) == str:
            self.id = del_trx_id
            # check other params
            self.content = "OBJECT_STATUS_DELETED"
            for key in self.__dict__:
                if key not in ["type", "id", "content"]:
                    raise ParamOverflowError(f"del object got a no-need param {key}")

        if reply_trx_id and type(reply_trx_id) == str:
            self.inreplyto = {"trxid": reply_trx_id}
            if not (self.content or self.image):
                raise ParamRequiredError("content or image is needed.")

        if like_trx_id and type(like_trx_id) == str:
            self.id = like_trx_id
            # check other params: only id param is needed.
            for key in self.__dict__:
                if key != "id":
                    raise ParamTypeError(
                        403,
                        f"like or dislike object can only have id param. but param {key} is found.",
                    )


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
class WalletInfo:
    def __init__(self, wallet_id=None, wallet_type=None, wallet_name=None, **kwargs):
        self.id = wallet_id or kwargs.get("wallet_id")
        self.type = wallet_type or kwargs.get("wallet_type", "mixin")
        self.name = wallet_name or kwargs.get("wallet_name", "mixinmessenger")


@dataclasses.dataclass
class PersonObj(NewTrxObject):
    """activity.person object; for user to update profile."""

    def __init__(
        self,
        name: str = None,
        image=None,
        wallet: Dict = None,
    ):
        if name:
            self.name = name
        if image:
            self.image = NewTrxImg(image).person_img()
        if wallet.get("wallet_id"):
            self.wallet = [WalletInfo(**wallet).__dict__]
        if not (name or image or wallet):
            raise ParamRequiredError(
                403,
                "update person profile needs at least one of name or image or wallet.",
            )


@dataclasses.dataclass
class NewTrx:
    def __init__(self, activity_type, group_id, obj=None, **kwargs):
        self.type = activity_type
        if self.type not in [4, "Add", "Like", "Dislike", "Update"]:
            raise ParamValueError(
                403,
                f"{self.type} is not one of 4,Add,Like,Dislike... check the input params or update the rumpy code. ",
            )

        if group_id:
            self.target = {"id": group_id, "type": "Group"}
        else:
            raise ParamRequiredError("group_id param is need.")

        if isinstance(obj, PersonObj):
            self.person = obj.__dict__
        elif isinstance(obj, NewTrxObject):
            self.object = obj.__dict__
        elif isinstance(obj, dict):
            if self.type == "Add" and "type" not in obj:
                raise ParamRequiredError("obj need a `type` such as: `Note` or `File`")
            self.object = NewTrxObject(**obj).__dict__
        else:
            self.object = NewTrxObject(**kwargs).__dict__
