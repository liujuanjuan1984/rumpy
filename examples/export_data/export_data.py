import os
import datetime
import uuid
import sys
from officepy import JsonFile, Dir, Img, Stime
from rumpy import RumClient
from rumpyconfig import RumpyConfig
from typing import List, Dict


def _person_name(trx_id_or_pubkey, trxs, since=None, client=None):
    """get the lastest name of the person published the trx_id"""
    key = "SenderPubkey" if "Publisher" not in trxs[0] else "Publisher"
    if trx_id_or_pubkey.endswith("=="):
        pubkey = trx_id_or_pubkey
    else:
        trx_id = trx_id_or_pubkey
        trxdata = client.group.trx(trx_id)
        pubkey = (
            trxdata.get("Publisher") or trxdata.get("SenderPubkey") or trx_id_or_pubkey
        )

    rlt = []
    for trxdata in trxs:
        if trxdata[key] == pubkey and trxdata["TypeUrl"] == "quorum.pb.Person":
            rlt.append(trxdata)
    since = since or datetime.datetime.now()

    name = ""
    for trxdata in rlt:
        name = trxdata["Content"].get("name") or ""
        if Stime.ts2datetime(trxdata.get("TimeStamp")) <= since:
            return name
    return name


def trx_export(trxdata: Dict, trxs: List) -> Dict:
    """export data with refer_to data"""
    ts = Stime.ts2datetime(trxdata.get("TimeStamp"))
    info = {
        "trx_id": trxdata["TrxId"],
        "trx_time": str(ts),
        "trx_type": client.group.trx_type(trxdata),
    }

    _content = trxdata["Content"]
    if "id" in _content:
        jid = _content["id"]
        info["refer_to"] = {
            "trx_id": jid,
            "text": trxdata["Content"].get("content") or "",
            "name": _person_name(jid, trxs, ts, client),
        }
    elif "inreplyto" in _content:
        jid = _content["inreplyto"]["trxid"]
        info["refer_to"] = {
            "trx_id": jid,
            "text": trxdata["Content"].get("content") or "",
            "name": _person_name(jid, trxs, ts, client),
        }

    if "content" in _content:
        info["text"] = _content["content"]
    if "image" in _content:
        if type(_content["image"]) == dict:
            info["imgs"] = [_content["image"]]
        else:
            info["imgs"] = _content["image"]
    return info


def export():
    my_trxs = {}

    # 获取本人发布的所有数据
    for gdata in client.node.groups():
        pubkey = gdata["user_pubkey"]
        group_id = gdata["group_id"]
        key = (group_id, gdata["group_name"])
        my_trxs[key] = []
        client.group_id = group_id
        trxs = client.group.content()
        for trxdata in trxs:
            if trxdata["Publisher"] == pubkey:
                my_trxs[key].append(trxdata)

    # 把这些数据转换为 markdown 和图片，并保存在本地目录

    # 把不同trxtype的数据导出，图片decode包装为方法
    for group_id, group_name in my_trxs:
        gtrxs = my_trxs[(group_id, group_name)]
        if not gtrxs:
            continue
        gfile = f"{JSON_DIR}\\{group_name}_{group_id}_{datetime.date.today()}.json"
        gdata = []
        client.group_id = group_id
        trxs = client.group.content()
        for trxdata in gtrxs:
            gdata.append(trx_export(trxdata, trxs))
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
        jnote = [f"<!--group_id:{gid} update_at:{gtime}-->\n\n# {gname}\n\n"]

        for i in idata:
            jnote.append(_trans(i))

        author = f"\n<!--bot author: liujuanjuan1984, https://github.com/liujuanjuan1984/rumpy -->\n"
        jnote.append(author)
        with open(jfile, "w", encoding="utf-8") as f:
            f.writelines(jnote)


def export_text_daily(daystr):
    """从数据文件中把文本自动合并到本地随手写目录中"""
    todofiles = Dir(JSON_DIR).search_files_by_types(".json")
    homedir = r"D:\MY-OBSIDIAN-DATA\my_Writing\随手写"

    jfile = homedir + "\\" + daystr.replace("-", "_") + "_随手写.md"

    if os.path.exists(jfile):
        with open(jfile, "r", encoding="utf-8") as f:
            jnote = f.readlines()
    else:
        jnote = []

    for ifile in todofiles:
        for i in JsonFile(ifile).read():
            if i["trx_time"].find(daystr) >= 0:
                if "text" in i:
                    jline = "\n\n---\n\n" + i["text"] + "\n"
                    if "".join(jline) not in "".join(jnote):
                        jnote.append(jline)

    if len(jnote) == 0:
        return
    with open(jfile, "w", encoding="utf-8") as f:
        f.writelines(jnote)
    print(datetime.datetime.now(), jfile)


if __name__ == "__main__":

    # init
    client = RumClient(**RumpyConfig.GUI)
    nodeid = client.node.id
    SAVE_DIR = os.path.join(os.path.dirname(__file__), "data")
    JSON_DIR = os.path.join(SAVE_DIR, nodeid, "json")
    MD_DIR = os.path.join(SAVE_DIR, nodeid, "markdown")
    IMG_DIR = os.path.join(SAVE_DIR, nodeid, "markdown", "images")
    Dir(JSON_DIR).check()
    Dir(IMG_DIR).check()

    # 登入账号，并导出数据
    export()

    # 数据转换，从json转换为markdown，按种子网络来保存自己的所有动态。
    # trans()

    # 编程自由/days
    # D:\RUM2-DATA\rum-20211030
    if nodeid == "16Uiu2HAkytdk8dhP8Z1JWvsM7qYPSLpHxLCfEWkSomqn7Tj6iC2d":
        lastupdate = "2022-03-04"

    # 怒放、永远爱你、RUM小七
    # D:\RUM2-DATA\rum-20211122
    elif nodeid == "16Uiu2HAmLrpCred9yKoaq55hSRYktapzsBGv9ryMaHGEWfuCuaFT":
        lastupdate = "2022-03-04"

    # 送你一束小花花，刘娟娟的分身
    # D:\RUM2-DATA\rum-20220126
    elif nodeid == "16Uiu2HAm3KqGroNs9phdtU3GKH47t8XqeEvxAGcszn9z7Y3nVE9f":
        lastupdate = "2022-03-04"

    else:
        lastupdate = "2021-10-01"

    # 按天导出自己在各个组发的文本数据，按天来保存为文件。
    for i in range(0, -90, -1):
        daystr = str(datetime.date.today() + datetime.timedelta(days=i))
        if daystr >= lastupdate:
            export_text_daily(daystr)

    print(nodeid)
