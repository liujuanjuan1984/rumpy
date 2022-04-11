import base64
import uuid
import filetype
import io
import os
import datetime
from PIL import Image
from pygifsicle import gifsicle


class Img:
    """
    将图片转换为 RUM 支持的图片对象.

    以 rum-app 为例, 实际上是将图片编码为 base64 字符串, 以方便前端渲染
    """

    def __init__(self, img_paths):
        """
        img_paths: 图片路径, 单张是字符串, 多张是列表, 最多 4 张
            如果是设置头像, 组的图标等, 传一张图片; 发送图片则可多张
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
        with open(image, "rb") as f:
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
                out = img.resize((int(x * 0.95), int(y * 0.95)), Image.ANTIALIAS)
                im.close()
                im = io.BytesIO()
                out.save(im, "jpeg")
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
            gifsicle(
                gif,
                destination=destination,
                optimize=True,
                options=["--lossy=80", "--scale", str(n)],
            )
            if not cover:
                gif = destination
            size = os.path.getsize(gif) / 1024
            n -= 0.05

        return Img.image_to_bytes(gif)

    def group_icon(self):
        """将一张图片处理成组配置项 value 字段的值, 例如组的图标对象"""
        if self.img is None:
            raise ValueError("The parameter of Img should be the path of an image")
        img_bytes = Img.image_to_bytes(self.img)
        if filetype.guess(img_bytes).extension == "gif":
            zimg = Img.zip_gif(self.img, cover=False)
        else:
            zimg = Img.zip_image(img_bytes)
        icon = (
            f"data:{filetype.guess(zimg).mime};"
            f'base64,{base64.b64encode(zimg).decode("utf-8")}'
        )

        return icon

    def image_obj(self, kb=200):
        """将一张图片处理成 RUM 支持的图片对象, 例如用户头像, 要求大小小于 200kb

        kb: 设置图片大小, 需要小于 200kb
        """
        if self.img is None:
            raise ValueError("The parameter of Img should be the path of an image")
        img_bytes = Img.image_to_bytes(self.img)
        if filetype.guess(img_bytes).extension == "gif":
            zimg = Img.zip_gif(self.img, kb=kb, cover=False)
        else:
            zimg = Img.zip_image(img_bytes, kb=kb)
        im_obj = {
            "mediaType": filetype.guess(zimg).mime,
            "content": base64.b64encode(zimg).decode("utf-8"),
            "name": f"{uuid.uuid4()}-{datetime.datetime.now().isoformat()}",
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
