from PIL import Image
import base64
import io
import uuid
import datetime
import dataclasses
from typing import Any


class Img:
    def decode(self, content: str) -> bytes:
        """把 rum trx 中的图片内容即 content （经过编码的图片字节流）解码为图片字节流"""
        content = base64.b64decode(bytes(content, encoding="utf-8"))
        return Image.open(io.BytesIO(content))

    def save(self, content: str, imgpath: str) -> bytes:
        """把 rum trx 中的图片内容即 content （经过编码的图片字节流）解码后保存为本地文件"""
        return self.decode(content).save(imgpath)

    def encode(self, imgpath_or_imgbytes_or_trximgobj):
        return ImgObj(imgpath_or_imgbytes_or_trximgobj).__dict__


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
