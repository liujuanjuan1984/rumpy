# -*- coding: utf-8 -*-

import os
import datetime
import uuid
import sys

sys.path.append(os.path.realpath("."))

from rumpy import RumClient, JsonFile, Dir, Img
from examples.config import client_params


def export():
    my_trxs = {}

    # 获取本人发布的所有数据
    for gdata in client.node.groups():
        pubkey = gdata["user_pubkey"]
        group_id = gdata["group_id"]
        key = (group_id, gdata["group_name"])
        my_trxs[key] = []
        trxs = client.group.content(group_id)
        for trxdata in trxs:
            if trxdata["Publisher"] == pubkey:
                my_trxs[key].append(trxdata)

    # 把这些数据转换为 markdown 和图片，并保存在本地目录

    # 把不同trxtype的数据导出，图片decode包装为方法
    for group_id, group_name in my_trxs:
        gtrxs = my_trxs[(group_id, group_name)]
        if group_name != "刘娟娟的朋友圈":  # 测试用途，限定了只导出自己想要的组
            continue
        if gtrxs == []:
            continue
        gfile = f"{JSON_DIR}\\{group_name}_{group_id}_{datetime.date.today()}.json"
        gdata = []
        trxs = client.group.content(group_id)
        for trxdata in gtrxs:
            gdata.append(client.trx.export(trxdata, trxs))
        JsonFile(gfile).write(gdata)


def _save_img(imgs):
    lines = []
    for i in imgs:
        ixname = f"{uuid.uuid4()}-{datetime.date.today()}"  # 图片名字
        Img().save(i["content"], f"{IMG_DIR}\\{ixname}.png")  # 保存图片
        lines.append(f"\n\n![](./images/{ixname}.png)\n\n")  # 文本
    return "".join(lines)


def _quote_text(text):
    return "".join(["> ", "\n> ".join(text.split("\n")), "\n\n"])


def _trans(one):

    lines = [f"\n### {one['trx_time']}\n\n"]

    _info = {"like": "赞", "dislike": "踩"}
    t = one["trx_type"]
    if t in _info:
        name = one["refer_to"]["name"] or "某人"
        lines.append(f'<font color="darkred">点{_info[t]}给 `{name}` 发布的内容。</font>\n\n')
        if "text" in one["refer_to"]:
            lines.append(_quote_text(one["refer_to"]["text"]))
        if "imgs" in one["refer_to"]:
            lines.append(_save_img(one["refer_to"]["imgs"]))

    elif t == "person":
        lines.append(f'<font color="darkred">修改了个人信息。</font>\n\n')

    elif t == "annouce":
        lines.append(f'<font color="darkred">处理了链上请求。</font>\n\n')
    elif t == "reply":
        lines.append(f'<font color="darkred">发布了回复：</font>\n\n')
        if "text" in one:
            lines.append(one["text"])
        if "imgs" in one:
            lines.append(_save_img(one["imgs"]))

        name = one["refer_to"]["name"] or "某人"
        lines.append(f'\n\n<font color="darkred">回复给 `{name}` 所发布的内容：</font>\n\n')

        if "text" in one["refer_to"]:
            lines.append(_quote_text(one["refer_to"]["text"]))

        if "imgs" in one["refer_to"]:
            lines.append(_save_img(one["imgs"]))

    else:
        lines.append(f'<font color="darkred">发布了内容：</font>\n\n')
        if "text" in one:
            lines.append(_quote_text(one["text"]))
        if "imgs" in one:
            lines.append(_save_img(one["imgs"]))

    lines.append(f"\n<!--trx_id:{one['trx_id']}-->\n")

    return "".join(lines)


def trans():
    todofiles = Dir(JSON_DIR).search_files_by_types(".json")
    for ifile in todofiles:
        idata = JsonFile(ifile).read()
        jfile = ifile.replace(JSON_DIR, MD_DIR).replace(".json", ".md")
        gname, gid, gtime = ifile.replace(f"{JSON_DIR}\\", "").split("_")
        if gname != "刘娟娟的朋友圈":  # 测试用途，限定了只导出自己想要的组
            continue
        jnote = [f"<!--group_id:{gid} update_at:{gtime}-->\n\n# {gname}\n\n"]

        for i in idata:
            jnote.append(_trans(i))

        author = f"\n<!--bot author: liujuanjuan1984, https://github.com/liujuanjuan1984/rumpy -->\n"
        jnote.append(author)
        with open(jfile, "w", encoding="utf-8") as f:
            f.writelines(jnote)


if __name__ == "__main__":

    client = RumClient(**client_params)
    SAVE_DIR = r"D:\Jupyter\rumpy\examples\export_data\data"
    JSON_DIR = f"{SAVE_DIR}\\json"
    MD_DIR = f"{SAVE_DIR}\\markdown"
    IMG_DIR = f"{SAVE_DIR}\\markdown\\images"
    Dir(JSON_DIR).check_dir()
    Dir(IMG_DIR).check_dir()
    export()
    trans()
