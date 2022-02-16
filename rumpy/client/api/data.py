import dataclasses
from typing import Dict, List, Any
from PIL import Image
import base64
import io
import uuid
import datetime
import dataclasses
from typing import Any


@dataclasses.dataclass
class ImgObj:
    content: Any
    mediaType: str = "image/png"
    name: str = f"{uuid.uuid4()}-{str(datetime.datetime.now())[:19]}"

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
                self.mediaType = tgt["mediaType"]
                self.content = tgt["content"]
                self.name = tgt["name"]
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
    consensus_type: str
    encryption_type: str
    cipher_key: str
    app_key: str
    last_updated: int
    highest_height: int  # 区块数
    highest_block_id: str
    group_status: str


@dataclasses.dataclass
class DeniedlistUpdateParams:
    peer_id: str  # node_id ???QmQZcijmay86LFCDFiuD8ToNhZwCYZ9XaNpeDWVWWJY222
    group_id: str
    action: str  # "del" or add


@dataclasses.dataclass
class AnnounceParams:
    """
    group_id:
    action: add or remove
    type: user or producer
    memo:

    {
        "group_id": "",
        "action": "add",
        "type": "user",
        "memo": ""
    }
    """

    group_id: str
    action: str
    type: str
    memo: str


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


@dataclasses.dataclass
class UserUpdateParams:
    """
    {
        "user_pubkey": "",
        "group_id": "",
        "action": "add",
    }
    """

    user_pubkey: str
    group_id: str
    action: str  # "add" or "remove"
