import dataclasses
from typing import Dict, List, Any
from rumpy.img import Img


@dataclasses.dataclass
class ClientParams:
    """
    :param appid, str, Rum 客户端标识，自定义，随便写
    :param port, int, Rum 服务 端口号
    :param host,str, Rum 服务 host，通常是 127.0.0.1
    :param crtfile, str, Rum 的 server.crt 文件的绝对路径
    """

    port: int
    crtfile: str
    host: str = "127.0.0.1"
    appid: str = "peer"
    jwt_token: str = None


@dataclasses.dataclass
class ContentObjParams:
    """
    content: str,text
    name:str, title for group_post if need
    image: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs
    inreplyto:str,trx_id
    type: `Note`
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
                ximgs.append(Img().encode(img))
            self.image = ximgs

        if self.inreplyto != None:
            self.inreplyto = {"trxid": self.inreplyto}


@dataclasses.dataclass
class ContentParams:
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
    """

    group_id: str
    action: str
    type: str
    memo: str


@dataclasses.dataclass
class ProducerUpdateParams:
    producer_pubkey: str
    group_id: str
    action: str  # "add" or "remove"


@dataclasses.dataclass
class UserUpdateParams:
    user_pubkey: str
    group_id: str
    action: str  # "add" or "remove"


@dataclasses.dataclass
class CreateGroupParam:
    """app_key: 可以为自定义字段，只是如果不是 group_timeline,group_post,group_note 这三种，可能无法在 rumapp 中识别，如果是自己开发客户端，则可以自定义类型"""

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
class NodeInfo:
    node_id: str
    node_publickey: str
    node_status: str
    node_type: str
    node_version: str
    peers: Dict
