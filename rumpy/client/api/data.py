import dataclasses
from typing import Dict, List, Any
from PIL import Image
import base64
import io
import uuid
import time
import datetime


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
class CreateGroupParam:
    """
    app_key: 可以为自定义字段，只是如果不是 group_timeline,group_post,group_note 这三种，可能无法在 rumapp 中识别，如果是自己开发客户端，则可以自定义类型

    {
        "group_name": "",
        "consensus_type": "poa",
        "encryption_type": "private",
        "app_key":"group_timeline"
    }

    """

    group_name: str
    consensus_type: str = "poa"
    encryption_type: str = "public"
    app_key: str = "group_timeline"

    def __post_init__(self):
        if self.consensus_type not in ["poa"]:  # ["poa","pos","pow"]:
            self.consensus_type = "poa"
        if self.encryption_type not in ["public", "private"]:
            self.encryption_type = "public"
        # if self.app_key not in ["group_timeline", "group_post", "group_note"]:
        #    self.app_key = "group_timeline"


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
class ImgObj:
    content: Any
    mediaType: str = "image/png"
    name: str = f"{uuid.uuid4()}-{round(int(time.time()*1000000))}"

    def __post_init__(self):
        tgt = self.content
        try:
            if type(tgt) == str:
                with open(tgt, "rb") as f:
                    self.content = self.encode(f.read())
                self.mediaType = tgt.split(".")[-1]
            elif type(tgt) == bytes:
                self.content = self.encode(tgt)
            elif type(tgt) == dict:
                self.mediaType = tgt.get("mediaType") or "image/png"
                self.content = tgt.get("content") or ""
                self.name = tgt.get("name") or f"{datetime.date.today()}"
        except Exception as e:
            print(e)
            return print(tgt, "must be imgpath or imgbytes")

    def encode(self, imgbytes):
        return base64.b64encode(imgbytes).decode("utf-8")


@dataclasses.dataclass
class ContentObjParams:
    """
    content: str,text
    name:str, title for group_post if need
    image: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs
    inreplyto:str,trx_id
    type: `Note`

    {
        "type":"Note"
        "content":"text content",
        "name":"title",
        "image":[],
        "inreplyto":{
            "trx_id":""
        },
    }

    """

    content: str = None
    name: str = None
    image: List = None
    inreplyto: Any = None
    type: str = "Note"

    def __post_init__(self):
        if self.image != None:
            ximgs = []
            for img in self.image:
                ximgs.append(ImgObj(img).__dict__)
            self.image = ximgs

        if self.inreplyto != None:
            self.inreplyto = {"trxid": self.inreplyto}


@dataclasses.dataclass
class ContentParams:
    """
    {
        "type":"Add"
        "object":{},
        "target":{
            "id": "",
            "type": "Group",
            }
    }
    """

    type: Any
    object: Dict
    target: str  # group_id

    def __post_init__(self):
        if self.type not in [4, "Add", "Like", "Dislike"]:
            self.type = "Add"
        self.target = {"id": self.target, "type": "Group"}


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
    highest_height: int  # 区块数
    highest_block_id: str
    group_status: str


@dataclasses.dataclass
class ProducerUpdateParams:
    """
    {
        "producer_pubkey": "",
        "group_id": "",
        "action": "add",
    }
    """

    producer_pubkey: str
    group_id: str
    action: str  # "add" or "remove"
