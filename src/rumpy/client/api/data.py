import base64
import uuid
import filetype
import time
import io
import os
import json
import datetime
import dataclasses
from PIL import Image
from pygifsicle import gifsicle
from typing import Dict, List, Any

TRX_TYPES = [
    "POST",
    "ANNOUNCE",
    "REQ_BLOCK_FORWARD",
    "REQ_BLOCK_BACKWARD",
    "BLOCK_SYNCED",
    "BLOCK_PRODUCED",
    "ASK_PEERID",
]


class Img:
    """
    将图片转换为 RUM 支持的图片对象
    """
    def __init__(self, img_paths):
        """
        img_paths: 图片路径, 单张是字符串, 多张是列表, 最多 4 张
            如果是设置头像, 组的图标等, 传一张图片, 发送图片则可多张
        """
        self.img = None
        self.imgs = img_paths
        if isinstance(img_paths, str):
            self.img = img_paths
            self.imgs = [img_paths]

    @staticmethod
    def image_to_bytes(image):
        """获取图片字节
        
        image: 图片路径
        """
        with open(image, 'rb') as f:
            img_bytes = f.read()
        return img_bytes

    @staticmethod
    def zip_image(img_bytes, kb=200):
        """压缩图片(非动图)到指定大小 (kb) 以下
        
        img_bytes: 图片字节
        kb: 指定压缩大小, 默认 200kb
        
        返回压缩后的图片字节
        """
        with io.BytesIO(img_bytes) as im:
            size = len(im.getvalue()) / 1024
            if size < kb:
                return img_bytes
            while size >= kb:
                img = Image.open(im)
                x, y = img.size
                out = img.resize((int(x * 0.95), int(y * 0.95)),
                                 Image.ANTIALIAS)
                im.close()
                im = io.BytesIO()
                out.save(im, 'jpeg')
                size = len(im.getvalue()) / 1024
            return im.getvalue()

    @staticmethod
    def zip_gif(gif, kb=200, cover=False):
        """压缩动图(gif)到指定大小(kb)以下
        
        gif: gif 格式动图本地路径
        kb: 指定压缩大小, 默认 200kb
        cover: 是否覆盖原图, 默认不覆盖

        返回压缩后图片字节. 该方法需要安装 gifsicle 软件和 pygifsicle 模块
        """

        size = os.path.getsize(gif) / 1024
        if size < kb:
            return Img.image_to_bytes(gif)

        destination = None
        if not cover:
            destination = f"{os.path.splitext(gif)[0]}-zip.gif"

        n = 0.9
        while size >= kb:
            gifsicle(gif,
                     destination=destination,
                     optimize=True,
                     options=["--lossy=80", "--scale",
                              str(n)])
            if not cover:
                gif = destination
            size = os.path.getsize(gif) / 1024
            n -= 0.05

        return Img.image_to_bytes(gif)

    def group_icon(self):
        """将一张图片处理成组配置项的 value 字段值, 例如组的图标对象"""
        img_bytes = Img.image_to_bytes(self.img)
        if filetype.guess(img_bytes).extension == "gif":
            zimg = Img.zip_gif(self.img, cover=False)
        else:
            zimg = Img.zip_image(img_bytes)
        icon = (f'data:{filetype.guess(zimg).mime};'
                f'base64,{base64.b64encode(zimg).decode("utf-8")}')

        return icon

    def image_obj(self, kb=200):
        """将一张图片处理成 RUM 支持的图片对象, 例如用户头像, 要求大小小于 200kb
        
        kb: 设置图片大小, 需要小于 200kb
        """
        img_bytes = Img.image_to_bytes(self.img)
        if filetype.guess(img_bytes).extension == "gif":
            zimg = Img.zip_gif(self.img, kb=kb, cover=False)
        else:
            zimg = Img.zip_image(img_bytes, kb=kb)
        im_obj = {
            "mediaType": filetype.guess(zimg).mime,
            "content": base64.b64encode(zimg).decode("utf-8"),
            "name": f"{uuid.uuid4()}-{datetime.datetime.now().isoformat()}"
        }
        return im_obj

    def image_objs(self):
        """将一张或多张图片处理成 RUM 支持的图片对象列表, 要求总大小小于 200kb"""
        kb = int(200 // len(self.imgs))
        im_objs = []
        for i in self.imgs:
            image = Img.image_obj(i, kb=kb)
            im_objs.append(image)

        return im_objs


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
    highest_height: int  # 区块数
    highest_block_id: str
    group_status: str
    snapshot_info: SnapShotInfo.__dict__


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
            d["wallet"] = [{
                "id": self.wallet,
                "type": "mixin",
                "name": "mixin messenger"
            }]

        if len(d) == 0:
            raise ValueError("Person must have name or image fields")
        self.__dict__ = d
