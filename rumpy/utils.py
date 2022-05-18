import datetime
import hashlib
import os
import io
import sys
import logging

IMAGE_MAX_SIZE_KB = 200  # kb 每条trx中所包含的图片总大小限制为 200


logger = logging.getLogger(__name__)


def sha256(ibytes):
    return hashlib.sha256(ibytes).hexdigest()


def read_file_to_bytes(file_path):

    if not os.path.exists(file_path):
        raise ValueError(f"{file_path} file is not exists.")

    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a file.")

    with open(file_path, "rb") as f:
        bytes_data = f.read()
    return bytes_data


def zip_image(img_bytes, kb=IMAGE_MAX_SIZE_KB):
    """压缩图片(非动图)到指定大小 (kb) 以下

    img_bytes: 图片字节
    kb: 指定压缩大小, 默认 200kb

    返回压缩后的图片字节
    """
    from PIL import Image

    kb = kb or IMAGE_MAX_SIZE_KB

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


def zip_gif(gif, kb=IMAGE_MAX_SIZE_KB, cover=False):
    """压缩动图(gif)到指定大小(kb)以下

    gif: gif 格式动图本地路径
    kb: 指定压缩大小, 默认 200kb
    cover: 是否覆盖原图, 默认不覆盖

    返回压缩后图片字节. 该方法需要安装 gifsicle 软件和 pygifsicle 模块
    """
    from pygifsicle import gifsicle

    kb = kb or IMAGE_MAX_SIZE_KB
    size = os.path.getsize(gif) / 1024
    if size < kb:
        return read_file_to_bytes(gif)

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

    return read_file_to_bytes(gif)


def zip_image_file(file_path, kb=IMAGE_MAX_SIZE_KB):
    import filetype

    img_bytes = read_file_to_bytes(file_path)
    try:
        if filetype.guess(img_bytes).extension == "gif":
            img_bytes = zip_gif(file_path, kb=kb, cover=False)
        else:
            img_bytes = zip_image(img_bytes, kb=kb)
    except Exception as e:
        logger.warning(f"{sys._getframe().f_code.co_name}, {e}")

    return img_bytes


def ts2datetime(timestamp):
    ts = int(timestamp)
    n = 10 ** (len(str(ts)) - 10)
    return datetime.datetime.fromtimestamp(int(ts / n))
