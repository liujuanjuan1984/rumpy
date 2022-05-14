import sys
import datetime
import time
import json
import os
import random
from sqlalchemy import Column, Integer, String, Boolean, distinct, and_
from config_rss import *
from modules import *
from rumpy import RumClient
from rumpy.client.module_op import BaseDB
from rumpy.client.module.base import Base
from rumpy.client.utils import ts2datetime

sys.path.insert(1, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data


"""
rss bot 是一个基于 mixin messenger 的 bot
本模块的功能是从 rum 网络获取待转发的数据，并根据用户与 rss bot 所发出的订阅要求，转发到 xin
"""


class RssBot:
    def __init__(self):
        self.rum = RumClient(port=rum_port)
        self.config = AppConfig.from_file(mixin_bot_config_file)
        self.xin = HttpClient_AppAuth(self.config)
        self.db = BaseDB("rss_bot_test", echo=False, reset=False)
        self.check_groups()
        self.groups = self.db.session.query(BotRumGroups).all()
        self.update_all_profiles()
        self.count_users()

    def update_profiles(self, group_id):
        self.rum.group_id = group_id
        _x = and_(BotRumProgress.group_id == group_id, BotRumProgress.progress_type == "GET_PROFILES")
        progress = self.db.session.query(BotRumProgress).filter(_x).first()

        if progress == None:
            _p = {"progress_type": "GET_PROFILES", "trx_id": None, "timestamp": None, "group_id": group_id}
            print(_p)
            self.db.add(BotRumProgress(_p))

        p_tid = None if progress == None else progress.trx_id
        print(datetime.datetime.now(), "update_profiles", group_id, p_tid)

        data = self.rum.group.get_users_profiles({"trx_id": p_tid}, ("name", "wallet"))
        tid = data.get("trx_id")
        ts = data.get("trx_timestamp")

        if tid and tid != p_tid:
            print(tid, ts)
            self.db.session.query(BotRumProgress).filter(_x).update({"trx_id": tid, "timestamp": ts})
            self.db.session.commit()

        for pubkey in data.get("data"):
            _name = data["data"][pubkey].get("name")
            _wallet = data["data"][pubkey].get("wallet")
            if type(_wallet) == list:
                _wallet = _wallet[0]["id"]
            _x = and_(BotRumProfiles.group_id == group_id, BotRumProfiles.pubkey == pubkey)
            existd = self.db.session.query(BotRumProfiles).filter(_x).first()
            if not existd:
                _p = {"group_id": group_id, "pubkey": pubkey, "name": _name, "wallet": _wallet, "timestamp": ts}
                self.db.add(BotRumProfiles(_p))
            elif existd.timestap < ts:
                _p = {"timestamp": ts}
                if _name != existd.name:
                    _p["name"] = _name
                if _wallet != existd.wallet:
                    _p["wallet"] = _wallet

                self.db.session.query(BotRumProfiles).filter(-x).update(_p)
                self.db.commit()

    def update_all_profiles(self):

        for g in self.groups:
            print(datetime.datetime.now(), g.minutes, g.group_id, g.group_name)
            self.update_profiles(g.group_id)

    def check_groups(self):

        # BotRumGroups init or update.
        for k in commands:
            _gid = commands[k]["group_id"]
            if _gid not in (None, -1):
                self.rum.group_id = _gid
                existd = self.db.session.query(BotRumGroups).filter(BotRumGroups.group_id == _gid).first()
                _m = commands[k].get("minutes") or -30
                if existd is None:
                    _p = {
                        "group_id": _gid,
                        "group_name": self.rum.group.seed().get("group_name"),
                        "minutes": _m,
                    }
                    self.db.add(BotRumGroups(_p))
                elif existd.minutes != _m:
                    self.db.session.query(BotRumGroups).filter(BotRumGroups.group_id == _gid).update({"minutes": _m})
                    self.db.commit()

    def count_users(self):

        print("🤖 Rss Rum to Xin bot 7000104017 🤖")
        print("=== 每个种子网络的订阅数 ===")
        counts = {}
        for g in self.groups:
            _c = self.db.session.query(BotRss).filter(BotRss.group_id == g.group_id).all()
            counts[g.group_name] = len(_c)
        countsit = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for name, n in countsit:
            print(n, name)

        _c = self.db.session.query(BotRss).filter(BotRss.user_id).all()
        print("🥂 共计", len(_c), "个用户使用 bot🥂")

    def get_nicknames(self, group_id):
        _nn = self.db.session.query(BotRumProfiles).filter(BotRumProfiles.group_id == group_id).all()
        nicknames = {}
        for _n in _nn:
            nicknames[_n.pubkey] = {"name": _n.name}
        return nicknames

    def get_trxs_from_rum(self):
        print(datetime.datetime.now(), "get_trxs_from_rum ...")

        for g in self.groups:
            self.rum.group_id = g.group_id
            if not self.rum.group.is_joined():
                print("WARN:", gid, "you are not in this group. pls join it.")
                continue

            nicknames = self.get_nicknames(g.group_id)
            existd = (
                self.db.session.query(BotRumProgress)
                .filter(and_(BotRumProgress.group_id == g.group_id, BotRumProgress.progress_type == "GET_CONTENT"))
                .first()
            )

            gname = g.group_name
            minutes = self.db.session.query(BotRumGroups.minutes).filter(BotRumGroups.group_id == g.group_id).first()
            if minutes[0] is None:
                minutes = -15
            else:
                minutes = minutes[0]
            if not existd:
                _trxs = self.rum.group.content_trxs(is_reverse=True, num=10)
                if len(_trxs) > 0:
                    trx_id = _trxs[-1]["TrxId"]
                    _ts = str(ts2datetime(_trxs[-1]["TimeStamp"]))
                else:
                    trx_id = None
                    _ts = None

                _p = {"progress_type": "GET_CONTENT", "trx_id": trx_id, "timestamp": _ts, "group_id": g.group_id}
                self.db.add(BotRumProgress(_p))
            else:
                trx_id = existd.trx_id

            trxs = self.rum.group.content_trxs(trx_id=trx_id, num=10)
            for trx in trxs:
                _tid = trx["TrxId"]
                trx_id = _tid
                self.db.session.query(BotRumProgress).filter(
                    and_(BotRumProgress.group_id == g.group_id, BotRumProgress.progress_type == "GET_CONTENT")
                ).update({"trx_id": trx_id})
                self.db.commit()
                existd2 = self.db.session.query(BotTrxs).filter(BotTrxs.trx_id == _tid).first()
                if existd2:
                    continue

                ts = str(ts2datetime(trx["TimeStamp"]))  # 只发距今xx小时的更新，间隔时间由配置文件控制
                if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=minutes)):
                    continue

                obj, can_post = self.rum.group.trx_to_newobj(trx, nicknames)
                if not can_post:
                    continue

                pubkey = trx["Publisher"]
                if pubkey not in nicknames:
                    username = pubkey[-10:-2]
                else:
                    username = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})" or pubkey[-10:-2]
                obj["content"] = f"{username}@{gname}\n{obj['content']}"

                _trx = {
                    "trx_id": _tid,
                    "group_id": g.group_id,
                    "timestamp": ts,
                    "text": obj["content"].encode().decode("utf-8"),
                }
                print(datetime.datetime.now(), "got new trx: ", _tid)
                self.db.add(BotTrxs(_trx))
        print(datetime.datetime.now(), "get_trxs_from_rum done.")

    def send_msg_to_xin(self):

        print(datetime.datetime.now(), "send_msg_to_xin ...")
        rss = self.db.session.query(BotRss).all()

        """ 
        # test:我订阅所有
        for g in self.groups:
            user_id = "bae95683-eabb-422f-9588-24dadffd0323"  # "b807ebea-4b46-4cf6-89c5-3a810ba9d32e"
            conversation_id = "e81c28a6-47aa-3aa0-97d2-62ac1754c90f"
            _d = {
                "user_id": user_id,
                "group_id": g.group_id,
                "is_rss": True,
                "user_group": user_id + g.group_id,
                "conversation_id": conversation_id,
            }
            self.db.add(BotRss(_d))
        """

        for r in rss:
            # if r.conversation_id != my_conversation_id:
            #    continue

            gid = r.group_id
            uid = r.user_id
            _g = self.db.session.query(BotRumGroups).filter(BotRumGroups.group_id == gid).first()
            if _g:
                minutes = _g.minutes
            else:
                minutes = -15
            nice_ts = str(datetime.datetime.now() + datetime.timedelta(minutes=minutes))
            trxs = self.db.session.query(BotTrxs).filter(BotTrxs.group_id == gid).all()
            if len(trxs) == 0:
                continue
            for trx in trxs:
                # trx 的时间较早，就不推送了
                if trx.timestamp <= nice_ts or trx.created_at <= nice_ts:
                    continue
                sent = (
                    self.db.session.query(BotTrxsSent)
                    .filter(
                        and_(
                            BotTrxsSent.trx_id == trx.trx_id,
                            BotTrxsSent.group_id == gid,
                            BotTrxsSent.is_sent == True,
                            BotTrxsSent.user_id == uid,
                        )
                    )
                    .first()
                )
                if sent:
                    continue

                # 点赞、点踩及修改个人信息这几类动态就不发给别人了(但仍推给我自己)；然后长推送也精简一点。
                if r.conversation_id != my_conversation_id:
                    if trx.text.find(" 点赞给 `") >= 0:
                        continue
                    if trx.text.find(" 点踩给 `") >= 0:
                        continue
                    if trx.text.find(" 修改了个人信息：") >= 0:
                        continue
                    if trx.text.find("OBJECT_STATUS_DELETED") >= 0:
                        continue

                    _lenth = 200
                    if len(trx.text) > _lenth:
                        trx.text = trx.text[:_lenth] + "...略..."

                msg = pack_message(pack_text_data(trx.text), r.conversation_id)

                resp = self.xin.api.send_messages(msg)
                # print(datetime.datetime.now(), r.conversation_id, trx.text[:30].replace("\n", " "), "...")

                if "data" in resp:
                    _d = {
                        "trx_id": trx.trx_id,
                        "group_id": r.group_id,
                        "user_id": r.user_id,
                        "conversation_id": r.conversation_id,
                        "is_sent": True,
                    }
                    self.db.add(BotTrxsSent(_d))

        print(datetime.datetime.now(), "send_msg_to_xin done.")

    def send_to_rum(self, group_id=my_rum_group):
        self.rum.group_id = group_id
        data = self.db.session.query(BotComments).filter(BotComments.is_to_rum == False).all()
        for r in data:
            resp = self.rum.group.send_note(content=r.text[3:])
            if "trx_id" not in resp:
                continue
            self.db.session.query(BotComments).filter(BotComments.message_id == r.message_id).update(
                {"is_to_rum": True}
            )
            self.db.commit()

    def do_rss(self):
        self.send_to_rum()
        self.send_msg_to_xin()
        self.get_trxs_from_rum()

    def get_reply_text(self, text):
        try:
            _num = int(text)
            _abs = abs(_num)
        except:
            return welcome_text, None

        if str(_abs) not in list(commands.keys()):
            return welcome_text, None

        irss = {}  # init
        for g in self.groups:
            irss[g.group_id] = None

        _gidx = commands[str(_abs)]["group_id"]
        if _gidx == None:  # 取消所有
            for _gid in irss:
                irss[_gid] = False
            reply_text = f"👌 Ok，您已取消订阅所有种子网络。{rum_adds}"
        elif _gidx == -1:  # 订阅所有
            for _gid in irss:
                irss[_gid] = True
            reply_text = f"✅ Yes，您已成功订阅所有种子网络。{rum_adds}"
        else:
            # 修改订阅：增加或推定
            self.rum.group_id = _gidx
            print(_gidx)
            _gname = self.rum.group.seed().get("group_name")
            if _num > 0:
                irss[_gidx] = True
                reply_text = f"✅ Yes，您已成功订阅 {_gname}{rum_adds}"
            else:
                # 取消订阅
                irss[_gidx] = False
                reply_text = f"👌 Ok，您已取消订阅{_gname}{rum_adds}"
        return reply_text, irss

    def update_rss(self, user_id, irss):
        if irss is None:
            return
        for group_id in irss:
            ug = user_id + group_id
            existd = self.db.session.query(BotRss).filter(BotRss.user_group == ug).first()
            if existd:
                if irss[group_id] != None and existd.is_rss != irss[group_id]:
                    self.db.session.query(BotRss).filter(BotRss.user_group == ug).update({"is_rss": irss[group_id]})
                    self.db.commit()

            else:
                data = {
                    "user_id": user_id,
                    "group_id": group_id,
                    "is_rss": irss[group_id],
                    "user_group": ug,
                    "conversation_id": self.xin.get_conversation_id_with_user(user_id),
                }
                self.db.add(BotRss(data))

    def check_str_param(self, text):
        if type(text) == str:
            return text
        if type(text) == dict:
            return json.dumps(text)
        return str(text)

    def to_send_to_rum(self, msgview):
        # 帮我自己代发到Rum：由我发出的，以代发：开头的，长度超出10的文本

        _c = {
            "message_id": msgview.message_id,
            "is_reply": False,
            "is_to_rum": None,
            "quote_message_id": msgview.quote_message_id,
            "conversation_id": msgview.conversation_id,
            "user_id": msgview.user_id,
            "text": self.check_str_param(msgview.data_decoded),
            "category": msgview.category,
            "timestamp": str(msgview.created_at),
        }

        self.db.add(BotComments(_c))
        is_to_rum = (
            msgview.conversation_id == my_conversation_id
            and len(msgview.data_decoded) > 10
            and msgview.data_decoded.startswith("代发：")
        )
        if is_to_rum:

            self.db.session.query(BotComments).filter(BotComments.message_id == msgview.message_id).update(
                {"is_reply": True, "is_to_rum": False}
            )
            self.db.commit()
        return is_to_rum

    def counts_trxs(self, days=-1, num=100):
        """counts trxs num of every pubkey published at that day.

        Args:
            days (int, optional): days of datetime.timedata. Defaults to -1 which means yesterday.
            num (int, optional): how many trxs to check once. Defaults to 100.

        Returns:
            {
                "data":{pubkey:num},
                "date": that_day_string
            }
        """

        thatday = datetime.datetime.now().date() + datetime.timedelta(days=days)

        while True:
            _trxs = self.rum.group.content_trxs(is_reverse=True, num=num)
            lastest_day = ts2datetime(_trxs[-1]["TimeStamp"]).date()
            if lastest_day < thatday:
                counts = {}
                for _trx in _trxs:
                    _day = ts2datetime(_trx["TimeStamp"]).date()
                    if _day == thatday:
                        _pubkey = _trx["Publisher"]
                        if _pubkey not in counts:
                            counts[_pubkey] = 1
                        else:
                            counts[_pubkey] += 1
                else:
                    counts_result = {"data": counts, "date": str(thatday)}
                break
            else:
                num += num

        return counts_result

    def airdrop_to_group(self, group_id, num_trxs=1, days=-1):
        self.rum.group_id = group_id
        group_name = self.rum.group.seed().get("group_name")
        print(datetime.datetime.now(), group_id, group_name, "...")

        counts_result = self.counts_trxs(days=days)
        date = datetime.datetime.now().date() + datetime.timedelta(days=days)
        memo = f"{date} Rum 种子网络空投"
        for pubkey in counts_result["data"]:
            # trxs 条数够了
            if counts_result["data"][pubkey] < num_trxs:
                continue

            existd = (
                self.db.session.query(BotRumProfiles)
                .filter(and_(BotRumProfiles.pubkey == pubkey, BotRumProfiles.wallet != None))
                .first()
            )

            if existd:  # 有钱包
                name = existd.name
                sent = (
                    self.db.session.query(BotAirDrops)
                    .filter(and_(BotAirDrops.mixin_id == existd.wallet, BotAirDrops.memo == memo))
                    .first()
                )
                if sent:  # 用钱包排重，不重复空投
                    continue

                _num = str(round(0.001 + random.randint(1, 100) / 1000000, 6))
                _a = {
                    "mixin_id": existd.wallet,
                    "group_id": group_id,
                    "pubkey": pubkey,
                    "num": str(_num),
                    "token": "RUM",
                    "memo": memo,
                    "is_sent": False,
                }
                r = self.xin.api.transfer.send_to_user(existd.wallet, rum_asset_id, _num, memo)

                if "data" in r:
                    print(existd.wallet, str(_num), "账户余额：", r.get("data").get("closing_balance"))
                    _a["is_sent"] = True

                self.db.add(BotAirDrops(_a))

    def airdrop_to_node(self, num_trxs=1, days=-1):
        for group_id in self.rum.node.groups_id:
            self.airdrop_to_group(group_id, num_trxs, days)

    def airdrop_to_bot(self, memo=None):
        _today = str(datetime.datetime.now().date())
        memo = memo or f"{_today} Rum 订阅器空投"
        users = self.db.session.query(distinct(BotRss.user_id)).all()
        for user in users:
            print(user)
            sent = (
                self.db.session.query(BotAirDrops)
                .filter(and_(BotAirDrops.mixin_id == user, BotAirDrops.memo == memo))
                .first()
            )
            if sent:  # 用钱包排重，不重复空投
                continue

            _num = str(round(0.00001 + random.randint(1, 10) / 1000000, 6))
            r = self.xin.api.transfer.send_to_user(user, rum_asset_id, _num, memo)
            _a = {"mixin_id": user, "num": str(_num), "token": "RUM", "memo": memo, "is_sent": False}
            if "data" in r:
                print(user, str(_num), "账户余额：", r.get("data").get("closing_balance"))
                _a["is_sent"] = True

            self.db.add(BotAirDrops(_a))


bot = RssBot()
