import dataclasses
import time
import base64
import json
import uuid
import time
import os
from typing import Dict, List, Any
from rumpy.client import utiltools


TRX_TYPES = [
    "POST",
    "ANNOUNCE",
    "REQ_BLOCK_FORWARD",
    "REQ_BLOCK_BACKWARD",
    "BLOCK_SYNCED",
    "BLOCK_PRODUCED",
    "ASK_PEERID",
]


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
            raise ValueError("Person must have name or image fields")
        self.__dict__ = d


IMAGE_MAX_SIZE_KB = 200  # kb 每条trx中所包含的图片总大小限制为 200


@dataclasses.dataclass
class NewTrxImg:
    """将一张图片处理成 RUM 支持的图片对象, 例如用户头像, 要求大小小于 200kb

    kb: 设置图片大小, 需要小于 200kb
    """

    def __init__(self, file_path=None, file_bytes=None, kb=None):
        import filetype

        kb = kb or IMAGE_MAX_SIZE_KB

        if file_path == None and file_bytes == None:
            raise ValueError("need file_path or file_bytes")

        if file_path:
            file_bytes = utiltools.zip_image_file(file_path, kb)
            self.name = os.path.basename(file_path).encode().decode("utf-8")

        if file_bytes:
            extension = filetype.guess(file_bytes).extension
            name = f"{uuid.uuid4()}-{round(int(time.time()*1000000))}"
            self.name = ".".join([name, extension])

        self.mediaType = filetype.guess(file_bytes).mime
        self.content = base64.b64encode(file_bytes).decode("utf-8")


@dataclasses.dataclass
class NewTrxObject:
    """send note to a group. can be used to send: text only, image only,
    text with image, reply...etc

    content: str,text
    name:str, title for group_post if needed
    images: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs

    发送/回复内容到一个组(仅图片, 仅文本, 或两者都有)

    content: 要发送的文本内容
    name: 内容标题, 例如 rum-app 论坛模板必须提供的文章标题
    images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
        content 和 images 必须至少一个不是 None
    update_id: 自己已经发送成功的某条 Trx 的 ID, rum-app 用来标记, 如果提供该参数,
        再次发送一条消息, 前端将只显示新发送的这条, 从而实现更新(实际两条内容都在链上)
    inreplyto: 要回复的内容的 Trx ID, 如果提供, 内容将回复给这条指定内容

    返回值 {"trx_id": "string"}

    """

    def __init__(
        self,
        objtype=None,
        trx_id=None,
        content=None,
        images=None,
        name=None,
        inreplyto=None,
    ):
        self.type = objtype  # Note,File
        self.id = trx_id
        self.content = content

        if images:
            # 将一张或多张图片处理成 RUM 支持的图片对象列表, 要求总大小小于 200kb
            # 客户端限定：单条 trx 最多4 张图片
            kb = int(200 // min(len(images), 4))
            self.image = [NewTrxImg(file_path=file_path, kb=kb).__dict__ for file_path in images[:4]]

        self.name = name
        self.inreplyto = {"trxid": inreplyto} if inreplyto else None

        if self.type not in ["Note", "File"]:
            self.type = "Note"

        d = {}
        for key in self.__dict__:
            if self.__dict__[key]:
                d[key] = self.__dict__[key]
        self.__dict__ = d


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
    def __init__(self, sendtype=None, group_id=None, obj=None, **kwargs):
        self.type = sendtype
        if isinstance(obj, NewTrxObject):
            self.object = obj.__dict__
        elif isinstance(obj, dict):
            if "type" not in obj:
                raise ValueError("obj need a `type` such as: `Note` or `File`")
            self.object = obj
        else:
            self.object = NewTrxObject(**kwargs).__dict__
        self.target = {"id": group_id, "type": "Group"}

        if self.type not in [4, "Add", "Like", "Dislike"]:
            self.type = "Add"
