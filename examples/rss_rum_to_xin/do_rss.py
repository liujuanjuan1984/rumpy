"""
rss bot 是一个基于 mixin messenger 的 bot
本模块的功能是从 rum 网络获取待转发的数据，并根据用户与 rss bot 所发出的订阅要求，转发到 xin
"""

import datetime
import sys
import os
import random
import time
from rumpy import RumClient
from rumpy.client.utiltools import ts2datetime
from officy import JsonFile
from config_dev import (
    rum_port,
    rum_asset_id,
    mixin_sdk_dirpath,
    mixin_bot_config_file,
    rss_data_dir,
    my_conversation_id,
)

sys.path.insert(0, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from mixinsdk.types.message import pack_message, pack_text_data
from config_rss import commands, rum_adds, welcome_text


rum = RumClient(port=rum_port)
xin = HttpClient_BotAuth(BotConfig.from_file(mixin_bot_config_file))

# files_to_records_data
rum_groups_to_view_file = os.path.join(rss_data_dir, "rum_groups_to_view.json")
rss_file = os.path.join(rss_data_dir, "rss.json")
trxs_file = os.path.join(rss_data_dir, "rum_trxs_to_post.json")

# read data
rum_groups_to_view = JsonFile(rum_groups_to_view_file).read({})
rss = JsonFile(rss_file).read({})


def check_files():
    global rum_groups_to_view
    global rss
    # init data or checks
    if rum_groups_to_view == {}:
        for k in commands:
            _gid = commands[k]["group_id"]
            if _gid not in (None, -1):
                rum.group_id = _gid
                rum_groups_to_view[_gid] = {
                    "group_id": _gid,
                    "group_name": rum.group.seed()["group_name"],
                    "hours": commands[k].get("hours") or -1,
                }
        else:
            JsonFile(rum_groups_to_view_file).write(rum_groups_to_view)

    for gid in rum_groups_to_view:
        if gid not in rss:
            rss[gid] = {}
    else:
        JsonFile(rss_file).write(rss)

    # trxs data is large. split old data to other file. daily job.

    data = JsonFile(trxs_file).read({})
    _xday = str(datetime.datetime.now() + datetime.timedelta(hours=-24))
    oldfile = trxs_file.replace(".json", f"_{str(datetime.datetime.now().date())}.json")
    if os.path.exists(oldfile):
        return print(oldfile, "exists...")

    old = {}
    new = {}
    #
    for gid in data:
        old[gid] = {"progress": data[gid]["progress"], "data": {}, "update_at": str(datetime.datetime.now())}
        new[gid] = {"progress": data[gid]["progress"], "data": {}, "update_at": str(datetime.datetime.now())}
        for tid in data[gid]["data"]:
            if data[gid]["data"][tid]["trx_ts"] < _xday:
                old[gid]["data"][tid] = data[gid]["data"][tid]
            else:
                new[gid]["data"][tid] = data[gid]["data"][tid]
    JsonFile(trxs_file).write(new)
    JsonFile(oldfile).write(old)


def get_trxs_from_rum():
    global rum_trxs_to_post
    print(datetime.datetime.now(), "get_trxs_from_rum ...")
    # get rum data to post:
    for gid in rum_groups_to_view:
        rum.group_id = gid

        if not rum.group.is_joined():
            print("WARN:", gid, "you are not in this group. pls join it.")
            continue

        nicknames = rum.group.update_profiles(datadir=rss_data_dir, types=("name",)).get("data") or {}

        if gid not in rum_trxs_to_post:
            rum_trxs_to_post[gid] = {"progress": None, "data": {}}

        # 对于新的group，只从最新10条trxs来开始获取推送，避免数据量太大
        if rum_trxs_to_post[gid]["progress"] == None:

            _trxs = rum.group.content_trxs(is_reverse=True, num=10)
            if len(_trxs) > 0:
                rum_trxs_to_post[gid]["progress"] = _trxs[-1]["TrxId"]

        trxs = rum.group.content_trxs(trx_id=rum_trxs_to_post[gid]["progress"], num=10)

        for trx in trxs:
            _tid = trx["TrxId"]
            rum_trxs_to_post[gid]["progress"] = _tid

            if _tid in rum_trxs_to_post[gid]["data"]:
                continue

            ts = ts2datetime(trx["TimeStamp"])
            # 只发距今xx小时的更新，间隔时间由配置文件控制
            if str(ts) <= str(datetime.datetime.now() + datetime.timedelta(hours=rum_groups_to_view[gid]["hours"])):
                continue

            obj, can_post = rum.group.trx_to_newobj(trx, nicknames)
            if not can_post:
                continue

            gname = rum_groups_to_view[gid]["group_name"]
            pubkey = trx["Publisher"]
            if pubkey not in nicknames:
                username = pubkey[-10:-2]
            else:
                username = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})" or pubkey[-10:-2]

            obj["content"] = f"{username}@{gname}\n{obj['content']}"

            rum_trxs_to_post[gid]["data"][_tid] = {
                "trx_id": _tid,
                "trx_ts": str(ts),
                "data": obj["content"].encode().decode("utf-8"),
                "conversation_ids": [],
            }
            print(datetime.datetime.now(), "got new trx: ", _tid)

    JsonFile(trxs_file).write(rum_trxs_to_post)
    print(datetime.datetime.now(), "get_trxs_from_rum done.")
    return rum_trxs_to_post


def send_msg_to_xin():
    global rum_trxs_to_post
    print(datetime.datetime.now(), "send_msg_to_xin ...")

    for gid in rss:
        if gid not in rum_trxs_to_post:
            continue
        for conversation_id in rss[gid]:
            if rss[gid][conversation_id].get("conversation_id") != conversation_id:
                continue
            for tid in rum_trxs_to_post[gid]["data"]:
                if conversation_id in rum_trxs_to_post[gid]["data"][tid]["conversation_ids"]:
                    continue

                # trx 的时间较早，就不推送了
                _ts = str(datetime.datetime.now() + datetime.timedelta(hours=rum_groups_to_view[gid]["hours"]))
                if rum_trxs_to_post[gid]["data"][tid].get("trx_ts") <= _ts:
                    continue

                idata = rum_trxs_to_post[gid]["data"][tid]["data"]

                # 点赞、点踩及修改个人信息这几类动态就不发给别人了(但仍推给我自己)；然后长推送也精简一点。
                if conversation_id != my_conversation_id:
                    if idata.find(" 点赞给 `") >= 0:
                        continue
                    if idata.find(" 点踩给 `") >= 0:
                        continue
                    if idata.find(" 修改了个人信息：") >= 0:
                        continue

                    _lenth = 200
                    if len(idata) > _lenth:
                        idata = idata[:_lenth] + "...略..."

                msg = pack_message(pack_text_data(idata), conversation_id)
                try:
                    resp = xin.api.send_messages(msg)
                    print(datetime.datetime.now(), conversation_id, idata[:30].replace("\n", " "), "...")
                    if "data" in resp:
                        rum_trxs_to_post[gid]["data"][tid]["conversation_ids"].append(conversation_id)
                        JsonFile(trxs_file).write(rum_trxs_to_post)
                except Exception as e:
                    print(e)

    print(datetime.datetime.now(), "send_msg_to_xin done.")


def main():
    global rum_trxs_to_post
    global rss

    while True:
        print("+" * 100)
        print(datetime.datetime.now(), "new round begin ...")
        try:
            check_files()
            rum_trxs_to_post = JsonFile(trxs_file).read({})
            rss = JsonFile(rss_file).read({})
            get_trxs_from_rum()
            time.sleep(10)
            send_msg_to_xin()
            JsonFile(trxs_file).write(rum_trxs_to_post)
        except Exception as e:
            print(e)
        time.sleep(10)


if __name__ == "__main__":
    main()
