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
from config_dev import rum_port, mixin_sdk_dirpath

sys.path.insert(0, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from mixinsdk.types.message import pack_message, pack_text_data
from config_rss import *


rum = RumClient(port=rum_port)
xin = HttpClient_BotAuth(BotConfig.from_file(mixin_bot_config_file))
rum_groups_to_view = JsonFile(rum_groups_to_view_file).read({})


def get_trxs_from_rum(rum_trxs_to_post):

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


def send_msg_to_xin(rum_trxs_to_post):

    print(datetime.datetime.now(), "send_msg_to_xin ...")
    rss = JsonFile(rss_file).read({})
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
    return rum_trxs_to_post


def send_to_rum():
    data = JsonFile(send_to_rum_file).read({})
    for msgid in data:
        if "is_send" not in data[msgid]:
            resp = rum.group.send_note(content=data[msgid]["text"])
            if "trx_id" in resp:
                data[msgid]["send_at"] = str(datetime.datetime.now())
                JsonFile(send_to_rum_file).write(data)


def main():
    rum_trxs_to_post = JsonFile(trxs_file).read({})
    while True:
        print("+" * 100)
        print(datetime.datetime.now(), "new round begin ...")

        try:
            check_files()
            send_to_rum()
            rum_trxs_to_post = get_trxs_from_rum(rum_trxs_to_post)
            time.sleep(10)
            rum_trxs_to_post = send_msg_to_xin(rum_trxs_to_post)
        except Exception as e:
            print(e)
            JsonFile(trxs_file).write(rum_trxs_to_post)
        time.sleep(10)


if __name__ == "__main__":
    main()
