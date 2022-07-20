import base64
from dataclasses import dataclass, field, asdict
import json
import logging
import os
import time
from typing import Any, Dict, List, Union, Optional

import filetype
import rumpy.utils as utils
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


# 将一张或多张图片处理成 RUM 支持的图片对象列表, 要求总大小小于 200kb，此为链端限定
IMAGE_MAX_SIZE_KB = 200  # 200 kb 每条trx中所包含的图片总大小限制为 200
# 单条 trx 最多4 张图片；此为 rum app 客户端限定：第三方 app 调整该限定
IMAGE_MAX_NUM = 4
CHUNK_SIZE = 150 * 1024  # 150 kb，文件切割为多条trxs时，每条trx所包含的文件字节流上限


@dataclass
class URL:
    protocol: str = field(default="https", repr=False)  # repr 为 False 表示不显示在打印结果中，但可通过__dict__看到
    host: str = field(default="127.0.0.1", repr=False)
    port: int = field(default="8080", repr=False)
    path: str = field(default="", repr=False)
    url: str = field(default="", init=False)  # init 为 False 表示不可传入该参数

    def __post_init__(self):
        self.url = f"{self.protocol}://{self.host}:{self.port}{self.path}"


@dataclass
class ApiBaseURLS:
    FULL_NODE: str
    LIGHT_NODE: str
    PAYMENT_GATEWAY: str = "https://prs-bp2.press.one/api"

    def __init__(self, protocol="https", port=8080, host="127.0.0.1"):
        self.FULL_NODE = URL(protocol=protocol, host=host, port=port).url
        self.LIGHT_NODE = URL(protocol=protocol, host=host, port=port, path="/nodesdk_api").url


@dataclass
class NodeInfo:
    node_id: str
    node_publickey: str
    node_status: str
    node_type: str
    node_version: str
    peers: Dict


@dataclass
class Block:
    BlockId: str
    GroupId: str
    ProducerPubKey: str
    Hash: str
    Signature: str
    TimeStamp: str


@dataclass
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


@dataclass
class SnapShotInfo:
    TimeStamp: int
    HighestHeight: int
    HighestBlockId: str
    Nonce: int
    SnapshotPackageId: str
    SenderPubkey: str


@dataclass
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


@dataclass
class BaseData:
    def to_dict(self, with_keys=None, without_keys=None):
        rlt = {}
        for k, v in self.__dict__.items():
            if not v:
                continue
            if not without_keys and not with_keys:
                rlt[k] = v
                continue
            if with_keys and k in with_keys:
                rlt[k] = v
                continue
            if without_keys and k not in without_keys:
                rlt[k] = v
                continue
        return rlt


@dataclass
class NewTrxBase(BaseData):
    type: Union[str, int]
    target: Dict
    object: Optional[Dict] = None
    person: Optional[Dict] = None

    def __init__(self, type, group_id, object=None, person=None):
        self.target = {"id": group_id, "type": "Group"}

        if type not in [4, "Add", "Update", "Like", "Dislike"]:
            errmsg = f"{type} is not one of 4,Add,Like,Dislike... check the input params or update the rumpy code."
            raise ParamValueError(errmsg)
        self.type = type

        if not (object or person):
            errmsg = "need object or person param"
            raise ParamValueError(errmsg)
        elif object and person:
            err = "both object and person is given.only one needed"
            raise ParamOverflowError(err)
        elif object and isinstance(object, dict):
            self.object = object
        elif person and isinstance(person, dict):
            self.person = person
        else:
            err = "object or person param is required"
            raise ParamValueError(err)


@dataclass
class NewTrxLike(NewTrxBase):
    def __init__(self, trx_id, group_id, type="Like"):
        if type not in ("Like", "Dislike"):
            err = f"param type should be Like or Dislike"
            raise ParamOverflowError(err)
        object = {"id": trx_id}
        super().__init__(type, group_id, object=object)


@dataclass
class WalletInfo:
    id: str
    type: str = field(default="mixin")
    name: str = field(default="mixinmessenger")


@dataclass
class PersonWallets:
    rlt: Any

    def __post_init__(self):
        if isinstance(self.rlt, dict):
            self.rlt = [WalletInfo(**self.rlt).__dict__]
        elif isinstance(self.rlt, str):
            self.rlt = [WalletInfo(id=self.rlt).__dict__]
        else:
            raise ParamTypeError(
                "param wallet should be string for mixin_id or dict for wallet info with id,name,type",
            )


@dataclass
class ImgContent:
    name: str = None
    mediaType: str = None
    content: str = None

    def __init__(self, path_bytes_string, kb=None):

        if type(path_bytes_string) == dict:
            d = path_bytes_string
            self.content = d.get("content")
            if not self.content:
                err = f"ImgContent  type: {type(path_bytes_string)} ,content got null "
                raise ParamValueError(err)
            _bytes, _ = utils.get_filebytes(self.content)
            self.name = d.get("name", utils.filename_init(_bytes))
            self.mediaType = d.get("mediaType", filetype.guess(_bytes).mime)

        else:
            kb = kb or IMAGE_MAX_SIZE_KB
            self.name = utils.filename_init(path_bytes_string)
            file_bytes = utils.zip_image(path_bytes_string, kb)
            self.mediaType = filetype.guess(file_bytes).mime
            self.content = base64.b64encode(file_bytes).decode("utf-8")

    def person_img(self):
        return {"content": self.content, "mediaType": self.mediaType}


@dataclass
class PersonObj(BaseData):
    """activity.person object; for user to update profile."""

    name: str = None
    image: Union[str, List, Dict, None] = None
    wallet: Union[str, Dict, None] = None

    def __post_init__(self):
        if not (self.name or self.image or self.wallet):
            errmsg = "profile needs at least one of name or image or wallet."
            raise ParamRequiredError(errmsg)
        if self.image:
            self.image = ImgContent(self.image).person_img()
        if self.wallet:
            self.wallet = PersonWallets(self.wallet).rlt


@dataclass
class NewTrxPerson(NewTrxBase):
    def __init__(self, group_id, name=None, image=None, wallet=None):
        try:
            person = PersonObj(name, image, wallet).to_dict()
        except Exception as e:
            raise ParamValueError(e)
        super().__init__("Update", group_id, person=person)


@dataclass
class FileInfo:
    content: str
    mediaType: str
    compression: int = 0

    def __post_init__(self):
        if isinstance(self.content, bytes):
            self.content = base64.b64encode(self.content).decode("utf-8")
        else:
            raise ParamTypeError(f"content should be types type.now is {type(self.content)}")


@dataclass
class FileObj:
    name: str = None
    file: FileInfo.__dict__ = None
    type: str = "File"

    def __init__(self, content, mediaType, name):
        self.name = name
        self.file = FileInfo(content, mediaType).__dict__
        self.type = "File"


@dataclass
class NewTrxFile(NewTrxBase):
    def __init__(self, group_id, content, mediaType, name):
        try:
            object = FileObj(content, mediaType, name).__dict__
        except Exception as e:
            raise ParamValueError(e)
        super().__init__("Add", group_id, object=object)


@dataclass
class ContentObj(BaseData):
    type: str = "Note"
    content: str = None
    name: str = None
    image: List = None
    id: str = None
    inreplyto: Dict = None

    def __init__(
        self,
        content: str = None,
        name: str = None,
        images: List = None,
        edit_trx_id: str = None,
        del_trx_id: str = None,
        reply_trx_id: str = None,  # inreplyto
    ):
        """the object of activity (NewTrx params)

        Args:
            images (List, optional): list of ImgContent . Defaults to None.
            name (str, optional): used as title in bbs post. Defaults to None.
            reply_trx_id(str, optional): trx_id to reply. Defaults to None.
            edit_trx_id (str, optional): trx_id to edit or delete (just client show it). Defaults to None.
        """

        self.type = "Note"

        if content:
            if isinstance(content, str):
                self.content = content
            elif isinstance(content, (dict, list)):
                self.content = json.dumps(content)
            else:
                err = (f"new content type: {type(content)}. check the param or update rumpy code.",)
                raise ParamTypeError(err)

        if name and type(name) == str:
            self.name = name

        if images:
            kb = int(IMAGE_MAX_SIZE_KB // min(len(images), IMAGE_MAX_NUM))
            self.image = [ImgContent(i, kb=kb).__dict__ for i in images[:IMAGE_MAX_NUM]]

        if edit_trx_id and type(edit_trx_id) == str:
            self.id = edit_trx_id
            if not (self.content or self.image):
                raise ParamRequiredError("content or image is needed.")

        if reply_trx_id and type(reply_trx_id) == str:
            self.inreplyto = {"trxid": reply_trx_id}
            if not (self.content or self.image):
                raise ParamRequiredError("content or image is needed.")

        if del_trx_id and type(del_trx_id) == str:
            self.id = del_trx_id
            # check other params
            self.content = "OBJECT_STATUS_DELETED"
            for key, value in self.__dict__.items():
                if value and key not in ["type", "id", "content"]:
                    raise ParamOverflowError(f"del object got a no-need param {key}:{value}")


@dataclass
class NewTrxContent(NewTrxBase):
    def __init__(self, group_id, **kwargs):
        try:
            object = ContentObj(**kwargs).to_dict()
        except Exception as e:
            raise ParamValueError(e)
        super().__init__("Add", group_id, object=object)
