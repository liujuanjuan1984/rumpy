import base64
import datetime
import hashlib
import io
import json
import logging
import math
import os
from typing import Any, Dict, List

import certifi
import filetype
from PIL import Image

from rumpy.types.data import CHUNK_SIZE, IMAGE_MAX_SIZE_KB, TRX_TYPES, FileObj

logger = logging.getLogger(__name__)


def check_trx_mode(mode: str):
    if mode.lower() not in ["dny", "deny", "allow", "alw"]:
        raise ValueError(f"{mode} mode must be one of ['deny','allow']")
    if mode.lower() in ["dny", "deny"]:
        return "dny"
    if mode.lower() in ["alw", "allow"]:
        return "alw"


def check_trx_type(trx_type: str):
    if trx_type.upper() not in TRX_TYPES:
        raise ValueError(f"{trx_type} must be one of {TRX_TYPES}")
    return trx_type.lower()


def check_crtfile(crtfile):
    try:
        if not os.path.exists(crtfile):
            crtfile = certifi.where()
    except:
        crtfile = True
    return crtfile


def group_icon(file_path: str):
    """将一张图片处理成组配置项 value 字段的值, 例如组的图标对象"""

    img_bytes = zip_image_file(file_path)
    icon = f'data:{filetype.guess(img_bytes).mime}base64,{base64.b64encode(img_bytes).decode("utf-8")}'
    return icon


def quote_str(text):
    return "".join(["> ", "\n> ".join(text.split("\n")), "\n"]) if text else ""


def get_nickname(pubkey, nicknames):
    try:
        name = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})"
    except:
        name = pubkey[-10:-2] or "某人"
    return name


def read_file_to_bytes(file_path):

    if not os.path.exists(file_path):
        raise ValueError(f"{file_path} file is not exists.")

    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a file.")

    with open(file_path, "rb") as f:
        bytes_data = f.read()
    return bytes_data


def sha256(ibytes):
    return hashlib.sha256(ibytes).hexdigest()


def timestamp_to_datetime(timestamp):
    ts = int(timestamp)
    n = 10 ** (len(str(ts)) - 10)
    return datetime.datetime.fromtimestamp(int(ts / n))


def unique_trxs(trxs: List):
    """remove the duplicate trx from the trxs list"""
    new = {}
    for trx in trxs:
        if trx["TrxId"] not in new:
            new[trx["TrxId"]] = trx
    return [new[i] for i in new]


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


def zip_image(img_bytes, kb=IMAGE_MAX_SIZE_KB):
    """压缩图片(非动图)到指定大小 (kb) 以下

    img_bytes: 图片字节
    kb: 指定压缩大小, 默认 200kb

    返回压缩后的图片字节
    """

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


def zip_image_file(file_path, kb=IMAGE_MAX_SIZE_KB):

    img_bytes = read_file_to_bytes(file_path)
    try:
        if filetype.guess(img_bytes).extension == "gif":
            img_bytes = zip_gif(file_path, kb=kb, cover=False)
        else:
            img_bytes = zip_image(img_bytes, kb=kb)
    except Exception as e:
        logger.warning(f"zip_image_file {e}")

    return img_bytes


def split_file_to_trx_objs(file_path):
    file_total_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path).encode().decode("utf-8")
    file_obj = open(file_path, "rb")
    fileinfo = {
        "mediaType": filetype.guess(file_path).mime,
        "name": file_name,
        "title": file_name.split(".")[0],
        "sha256": sha256(file_obj.read()),
        "segments": [],
    }

    chunks = math.ceil(file_total_size / CHUNK_SIZE)
    objs = []

    for i in range(chunks):
        if i + 1 == chunks:
            current_size = file_total_size % CHUNK_SIZE
        else:
            current_size = CHUNK_SIZE
        file_obj.seek(i * CHUNK_SIZE)
        ibytes = file_obj.read(current_size)
        fileinfo["segments"].append({"id": f"seg-{i+1}", "sha256": sha256(ibytes)})
        obj = FileObj(
            name=f"seg-{i + 1}",
            content=ibytes,
            mediaType="application/octet-stream",
        )
        objs.append(obj)

    content = json.dumps(fileinfo).encode()
    obj = FileObj(content=content, name="fileinfo", mediaType="application/json")

    objs.insert(0, obj)
    file_obj.close()
    return objs


def merge_trxs_to_file(file_dir, info, trxs):
    ifilepath = os.path.join(file_dir, info["name"])
    if os.path.exists(ifilepath):
        logger.info(f" file exists {ifilepath}")
        return

    # _check_trxs
    right_shas = [i["sha256"] for i in info["segments"]]
    contents = {}

    for trx in trxs:
        content = base64.b64decode(trx["Content"]["file"]["content"])
        csha = hashlib.sha256(content).hexdigest()
        if csha in right_shas:
            contents[csha] = trx

    flag = True

    for seg in info["segments"]:
        if seg["sha256"] not in contents:
            logger.info(json.dumps(seg) + ", trx is not exists...")
            flag = False
            break
        if contents[seg["sha256"]]["Content"].get("name") != seg["id"]:
            logger.info(json.dumps(seg) + ", name is different...")
            flag = False
            break

    if flag:
        ifile = open(ifilepath, "wb+")
        for seg in info["segments"]:
            content = base64.b64decode(contents[seg["sha256"]]["Content"]["file"]["content"])
            ifile.write(content)
        ifile.close()
        logger.info(f"{ifilepath}, downloaded!")
