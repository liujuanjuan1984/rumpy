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

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for group_id, group_name in my_trxs:
        gtrxs = my_trxs[(group_id, group_name)]
        if gtrxs == []:
            continue
        today = str(datetime.datetime.now())[:10]
        gfile = f"{save_dir}\\json\\{group_name}_{group_id}_{today}.json"
        gdata = []
        trxs = client.group.content(group_id)
        for trxdata in gtrxs:
            gdata.append(client.trx.export(trxdata, trxs))
        JsonFile(gfile).write(gdata)


def _save_img(imgs, note):
    for i in imgs:
        ixname = f"{uuid.uuid4()}-{str(datetime.datetime.now())[:10]}"
        imgpath = f"{img_dir}\\{ixname}.png"
        Img().save(i["content"], imgpath)
        note += f"\n\n![](./images/{i['name']})\n\n"
    return note


def _trans(one):

    note = f"\n### " + one["trx_time"] + "\n\n"
    _info = {"like": "赞", "dislike": "踩"}
    t = one["trx_type"]
    if t in _info:
        name = one["refer_to"]["name"] or "某人"
        note += f'<font color="darkred">点{_info[t]}给 `{name}` 发布的内容。</font>\n\n'
        if "text" in one["refer_to"]:
            note += "> " + "\n> ".join(one["refer_to"]["text"].split("\n")) + "\n\n"
        if "imgs" in one["refer_to"]:
            note = _save_img(one["refer_to"]["imgs"], note)

    elif t == "person":
        note += '<font color="darkred">修改了个人信息。</font>\n\n'
    elif t == "annouce":
        note += '<font color="darkred">处理了链上请求。</font>\n\n'
    elif t == "reply":
        note += '<font color="darkred">发布了回复：</font>\n\n'
        if "text" in one:
            note += one["text"]
            # note += "    "+"\n    ".join(one['text'].split("\n")) +"\n"
        if "imgs" in one:
            note = _save_img(one["imgs"], note)

        name = one["refer_to"]["name"] or "某人"
        note += f'\n\n<font color="darkred">回复给 `{name}` 所发布的内容：</font>\n\n'
        if "text" in one["refer_to"]:
            note += "> " + "\n> ".join(one["refer_to"]["text"].split("\n")) + "\n\n"
        if "imgs" in one["refer_to"]:
            note = _save_img(one["refer_to"]["imgs"], note)

    else:
        note += '<font color="darkred">发布了内容：</font>\n\n'
        if "text" in one:
            # note += "    "+"\n    ".join(one['text'].split("\n")) +"\n"
            note += one["text"]
        if "imgs" in one:
            note = _save_img(one["imgs"], note)

    note += f"\n<!--trx_id:{one['trx_id']}-->\n"
    return note


def trans():
    todofiles = Dir(json_dir).search_files_by_types(".json")
    for ifile in todofiles:
        idata = JsonFile(ifile).read()
        jfile = ifile.replace(json_dir, md_dir).replace(".json", ".md")
        gname, gid, gtime = ifile.replace(json_dir + "\\", "").split("_")
        jnote = [f"<!--group_id:{gid} update_at:{gtime}-->\n\n# {gname}\n\n"]

        for i in idata:
            jnote.append(_trans(i))

        author = f"\n<!--bot author: liujuanjuan1984, https://github.com/liujuanjuan1984/rumpy -->\n"
        jnote.append(author)
        with open(jfile, "w", encoding="utf-8") as f:
            f.writelines(jnote)


if __name__ == "__main__":

    client = RumClient(**client_params)
    save_dir = r"D:\Jupyter\rumpy\Makefile\data"
    json_dir = save_dir + "\\json"
    md_dir = save_dir + "\\markdown"
    img_dir = save_dir + "\\markdown\\images"
    Dir(json_dir).check_dir()
    Dir(img_dir).check_dir()
    export()
    trans()
