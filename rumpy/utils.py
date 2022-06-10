import base64
import datetime
import hashlib
import io
import json
import logging
import math
import os
import uuid
from typing import Any, Dict, List
from urllib import parse

import certifi
import filetype
from PIL import Image

from rumpy.exceptions import *
from rumpy.types.data import *

logger = logging.getLogger(__name__)


def check_trx_mode(mode: str):
    if mode.lower() not in ["dny", "deny", "allow", "alw"]:
        raise ParamValueError(f"{mode} mode must be one of ['deny','allow']")
    if mode.lower() in ["dny", "deny"]:
        return "dny"
    if mode.lower() in ["alw", "allow"]:
        return "alw"


def check_trx_type(trx_type: str):
    if trx_type.upper() not in TRX_TYPES:
        raise ParamValueError(f"{trx_type} must be one of {TRX_TYPES}")
    return trx_type.lower()


def check_crtfile(crtfile):
    try:
        if not os.path.exists(crtfile):
            crtfile = certifi.where()
    except:
        crtfile = True
    return crtfile


def check_seed(seed: Dict):
    if is_seed(seed):
        return seed
    try:
        Seed(**seed)
    except Exception as e:
        raise RumChainException(f"{seed.get('error')}\n\n{e}")


def is_seed(seed: Dict) -> bool:
    try:
        Seed(**seed)
        return True
    except Exception as e:
        logger.error(f"{e}")
        return False


def group_icon(icon):
    """icon: one image as file path, or bytes, or bytes-string."""

    img_bytes = zip_image(icon)
    icon = f'data:{filetype.guess(img_bytes).mime};base64,{base64.b64encode(img_bytes).decode("utf-8")}'
    return icon


def quote_str(text):
    return "".join(["> ", "\n> ".join(text.split("\n")), "\n"]) if text else ""


def filename_init_from_bytes(file_bytes):
    extension = filetype.guess(file_bytes).extension
    name = f"{uuid.uuid4()}-{datetime.date.today()}"
    return ".".join([name, extension])


def filename_init(path_bytes_string):
    file_bytes, is_file = get_filebytes(path_bytes_string)
    if is_file:
        file_name = os.path.basename(path_bytes_string).encode().decode("utf-8")
    else:
        file_name = filename_init_from_bytes(file_bytes)
    return file_name


def get_nickname(pubkey, nicknames):
    try:
        name = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})"
    except:
        name = pubkey[-10:-2] or "某人"
    return name


def get_filebytes(path_bytes_string):
    _type = type(path_bytes_string)
    _size = len(path_bytes_string)
    is_file = False
    if _type == str:
        if os.path.exists(path_bytes_string):
            file_bytes = read_file_to_bytes(path_bytes_string)
            is_file = True
        else:
            file_bytes = base64.b64decode(path_bytes_string)
    elif _type == bytes:
        file_bytes = path_bytes_string
    else:
        raise ParamTypeError(f"not support for type: {_type} and length: {_size}")
    return file_bytes, is_file


def read_file_to_bytes(file_path):
    if not os.path.exists(file_path):
        raise ParamValueError(f"{file_path} file is not exists.")

    if not os.path.isfile(file_path):
        raise ParamValueError(f"{file_path} is not a file.")

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


def zip_image_bytes(img_bytes, kb=IMAGE_MAX_SIZE_KB):
    """zip image bytes and return bytes; default changed to .jpeg"""

    kb = kb or IMAGE_MAX_SIZE_KB
    guess_extension = filetype.guess(img_bytes).extension

    with io.BytesIO(img_bytes) as im:
        size = len(im.getvalue()) // 1024
        if size < kb:
            return img_bytes
        while size >= kb:
            img = Image.open(im)
            x, y = img.size
            out = img.resize((int(x * 0.95), int(y * 0.95)), Image.ANTIALIAS)
            im.close()
            im = io.BytesIO()
            try:
                out.save(im, "jpeg")
            except:
                out.save(im, guess_extension)
            size = len(im.getvalue()) // 1024
        return im.getvalue()


def zip_image(path_bytes_string, kb=IMAGE_MAX_SIZE_KB):
    file_bytes, is_file = get_filebytes(path_bytes_string)

    try:
        if filetype.guess(file_bytes).extension == "gif" and is_file:
            img_bytes = zip_gif(path_bytes_string, kb=kb, cover=False)
        else:
            img_bytes = zip_image_bytes(file_bytes, kb=kb)
    except Exception as e:
        logger.warning(f"zip_image {e}")
    return img_bytes


def split_file_to_trx_objs(path_bytes_string):
    file_bytes, _ = get_filebytes(path_bytes_string)
    total_size = len(file_bytes)
    file_name = filename_init(path_bytes_string)

    fileinfo = {
        "mediaType": filetype.guess(file_bytes).mime,
        "name": file_name,
        "title": file_name.split(".")[0],
        "sha256": sha256(file_bytes),
        "segments": [],
    }

    n = math.ceil(total_size / CHUNK_SIZE)
    chunks = [file_bytes[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE] for i in range(n)]
    objs = []
    for i in range(n):
        ibytes = file_bytes[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
        fileinfo["segments"].append({"id": f"seg-{i+1}", "sha256": sha256(ibytes)})
        objs.append(
            FileObj(
                name=f"seg-{i + 1}",
                content=ibytes,
                mediaType="application/octet-stream",
            )
        )
    content = json.dumps(fileinfo).encode()
    obj = FileObj(content=content, name="fileinfo", mediaType="application/json")
    objs.insert(0, obj)
    logger.info(f"{file_name} objs {len(objs)}...")
    return objs


def merge_trxs_to_file(file_dir, info, trxs):
    ifilepath = os.path.join(file_dir, info["name"])
    if os.path.exists(ifilepath):
        logger.info(f" file exists {ifilepath}")
        return
    logger.info(f"ifilepath {ifilepath} init..")
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


def merge_trxs_to_files(file_dir, infos, trxs):
    for info in infos:
        merge_trxs_to_file(file_dir, info, trxs)


def trx_typeurl(trx):
    typeurl = trx.get("TypeUrl")
    if typeurl == "quorum.pb.Person":
        return "Person"
    elif typeurl == "quorum.pb.Object":
        return "Object"
    return typeurl


def trx_type(trx: Dict):
    """get type of trx, trx is one of group content list"""
    typeurl = trx_typeurl(trx)
    if not typeurl:
        return "encrypted"
    if typeurl == "Person":
        return "person"
    content = trx.get("Content", {})
    trxtype = content.get("type", "other")
    if type(trxtype) == int:
        return "announce"
    if trxtype == "Note":
        if "inreplyto" in content:
            return "reply"
        if "image" in content:
            if "content" not in content:
                return "image_only"
            else:
                return "image_text"
        return "text_only"
    return trxtype.lower()  # "like","dislike","other"


def get_refer_trxid(trx):
    # 从trx中筛选出引用的 trx_id
    trxtype = trx_type(trx)
    if trxtype == "reply":
        refer_tid = trx["Content"]["inreplyto"]["trxid"]
    elif trxtype in ("like", "dislike"):
        refer_tid = trx["Content"]["id"]
    else:
        refer_tid = None
    return refer_tid


def _init_profile_status(trx_content):
    _name = "昵称" if "name" in trx_content else ""
    _wallet = "钱包" if "wallet" in trx_content else ""
    _image = "头像" if "image" in trx_content else ""
    _profile = "、".join([i for i in [_name, _image, _wallet] if i])
    return _profile


def _get_content(trx_content):
    _text = trx_content.get("content", "")
    _imgs = trx_content.get("image", [])
    return _text, _imgs


def trx_retweet_params_init(trx, refer_trx=None, nicknames={}):

    refer_trx = refer_trx or {}
    refer_pubkey = refer_trx.get("Publisher", "")
    refer_nickname = get_nickname(refer_pubkey, nicknames)  # TODO:nicknames 的处理和数据来源
    refer_text, refer_imgs = _get_content(refer_trx.get("Content", {}))

    trx_content = trx.get("Content", {})
    if not trx_content:
        return None
    trxtype = trx_type(trx)
    text, imgs = _get_content(trx_content)
    images = []
    lines = []

    if trxtype == "person":
        _profile = _init_profile_status(trx_content)
        lines.append(f"修改了个人信息：{_profile}。")
    elif trxtype == "file":
        lines.append("上传了文件。")
    elif trxtype == "announce":
        lines.append("处理了链上请求。")
    elif trxtype == "like":
        lines.append(f"点赞给 `{refer_nickname}` 所发布的内容：")
    elif trxtype == "dislike":
        lines.append(f"点踩给 `{refer_nickname}` 所发布的内容：")
    elif trxtype == "text_only":
        lines.insert(0, f"说：")
        lines.append(text)
    elif trxtype == "image_text":
        lines.insert(0, f"发布了图片，并且说：")
        lines.append(text)
        images.extend(imgs)
    elif trxtype == "image_only":
        lines.insert(0, f"发布了图片。")
        images.extend(imgs)
    elif trxtype == "reply":
        lines.insert(0, f"回复说：")
        if text:
            lines.append(text)
        if imgs:
            images.extend(imgs)
        lines.append(f"\n回复给 `{refer_nickname}` 所发布的内容：")

    if refer_text:
        lines.append(quote_str(refer_text))
    if refer_imgs:
        images.extend(refer_imgs)

    _dt = timestamp_to_datetime(trx.get("TimeStamp"))
    params = {"content": f"{_dt} " + "\n".join(lines), "images": images}
    return params


def get_url(base=None, endpoint=None, is_quote=False, **query_params):
    url = parse.urljoin(base, endpoint) if base else endpoint
    if query_params:
        for k, v in query_params.items():
            if type(v) == bool:
                query_params[k] = json.dumps(v)
        query_ = parse.urlencode(query_params)
        if is_quote:
            query_ = parse.quote(query_, safe="?&/")
        return "?".join([url, query_])
    return url


def last_trx_id(trx_id: str, trxs: List, reverse=False):
    """get the last-trx_id of trxs which if different from given trx_id"""
    # TODO: 不支持生成器，需要改写
    if reverse:
        _range = range(len(trxs))
    else:
        _range = range(-1, -1 * len(trxs), -1)
    for i in _range:
        tid = trxs[i]["TrxId"]
        if tid != trx_id:
            return tid
    return trx_id
