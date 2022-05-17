import sys
import datetime
import time
import json
import os
import random
from sqlalchemy import Column, Integer, String, Boolean, distinct, and_
from config import *
from modules import *
from rumpy import RumClient
from rumpy.client.module_op import BaseDB
from rumpy.client.module.base import Base
from rumpy.utils import ts2datetime

sys.path.insert(0, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data


class LuckyBot:
    def __init__(self):
        self.rum = RumClient(port=rum_port)
        self.rum.group_id = my_rum_group
        self.config = AppConfig.from_file(mixin_bot_config_file)
        self.xin = HttpClient_AppAuth(self.config)
        self.db = BaseDB("lucky_bot", echo=False, reset=False)

        self.update_profiles()

    def update_profiles(self, group_id=my_rum_group):
        self.rum.group_id = group_id
        _x = and_(BotRumProgress.group_id == group_id, BotRumProgress.progress_type == "GET_PROFILES")
        progress = self.db.session.query(BotRumProgress).filter(_x).first()

        if progress == None:
            _p = {"progress_type": "GET_PROFILES", "trx_id": None, "timestamp": None, "group_id": group_id}
            self.db.add(BotRumProgress(_p))

        p_tid = None if progress == None else progress.trx_id

        data = self.rum.group.get_users_profiles({"trx_id": p_tid}, ("name", "wallet"))
        tid = data.get("trx_id")
        ts = data.get("trx_timestamp")

        if tid and tid != p_tid:
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
            elif existd.timestamp < ts:
                _p = {"timestamp": ts}
                if _name != existd.name:
                    _p["name"] = _name
                if _wallet != existd.wallet:
                    _p["wallet"] = _wallet

                self.db.session.query(BotRumProfiles).filter(_x).update(_p)
                self.db.commit()

    def get_nicknames(self, group_id=my_rum_group):
        _nn = self.db.session.query(BotRumProfiles).filter(BotRumProfiles.group_id == group_id).all()
        nicknames = {}
        for _n in _nn:
            nicknames[_n.pubkey] = {"name": _n.name}
        return nicknames

    def get_trxs_from_rum(self, group_id=my_rum_group):
        print(datetime.datetime.now(), "get_trxs_from_rum ...")

        self.rum.group_id = group_id
        if not self.rum.group.is_joined():
            print("WARN:", gid, "you are not in this group. pls join it.")
            return

        nicknames = self.get_nicknames(group_id)
        existd = (
            self.db.session.query(BotRumProgress)
            .filter(and_(BotRumProgress.group_id == group_id, BotRumProgress.progress_type == "GET_CONTENT"))
            .first()
        )

        gname = my_rum_group_name
        if not existd:
            _trxs = self.rum.group.content_trxs(is_reverse=True, num=10)
            if len(_trxs) > 0:
                trx_id = _trxs[-1]["TrxId"]
                _ts = str(ts2datetime(_trxs[-1]["TimeStamp"]))
            else:
                trx_id = None
                _ts = None

            _p = {"progress_type": "GET_CONTENT", "trx_id": trx_id, "timestamp": _ts, "group_id": group_id}
            self.db.add(BotRumProgress(_p))
        else:
            trx_id = existd.trx_id

        trxs = self.rum.group.content_trxs(trx_id=trx_id, num=10)
        for trx in trxs:
            _tid = trx["TrxId"]
            trx_id = _tid
            self.db.session.query(BotRumProgress).filter(
                and_(BotRumProgress.group_id == group_id, BotRumProgress.progress_type == "GET_CONTENT")
            ).update({"trx_id": trx_id})
            self.db.commit()
            existd2 = self.db.session.query(BotTrxs).filter(BotTrxs.trx_id == _tid).first()
            if existd2:
                continue

            ts = str(ts2datetime(trx["TimeStamp"]))
            if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=default_minutes)):
                continue

            obj, can_post = self.rum.group.trx_to_newobj(trx, nicknames)
            if not can_post:
                continue

            pubkey = trx["Publisher"]
            _pubkey = pubkey[-10:-2]
            if pubkey in nicknames and username != _pubkey:
                username = nicknames[pubkey]["name"] + f"({_pubkey})"
            else:
                username = _pubkey

            # obj["content"] = f"{obj['content']}"

            _trx = {
                "trx_id": _tid,
                "group_id": group_id,
                "timestamp": ts,
                "text": obj["content"].encode().decode("utf-8"),
            }
            print(datetime.datetime.now(), "got new trx: ", _tid)
            self.db.add(BotTrxs(_trx))
        print(datetime.datetime.now(), "get_trxs_from_rum done.")

    def send_msg_to_xin(self):

        print(datetime.datetime.now(), "send_msg_to_xin ...")
        rss = self.db.session.query(BotRss).all()

        for r in rss:
            if r.is_rss != True:
                continue
            gid = r.group_id
            uid = r.user_id

            nice_ts = str(datetime.datetime.now() + datetime.timedelta(minutes=default_minutes))
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
                """ 
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
                """

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
                else:
                    print(resp)
                    self.reconnect()

        print(datetime.datetime.now(), "send_msg_to_xin done.")

    def send_to_rum(self, group_id=my_rum_group):
        self.rum.group_id = group_id
        data = self.db.session.query(BotComments).filter(BotComments.is_to_rum == False).all()
        for r in data:
            resp = self.rum.group.send_note(content=r.text[3:] + f"\n\n=={r.conversation_id}==")
            if "trx_id" not in resp:
                continue
            self.db.session.query(BotComments).filter(BotComments.message_id == r.message_id).update(
                {"is_to_rum": True}
            )
            self.db.commit()

    def do_rss(self):
        self.update_profiles()
        self.send_to_rum()
        self.send_msg_to_xin()
        self.get_trxs_from_rum()

    def get_reply_text(self, text):
        common_text = "👋 输入 你好 查看操作说明\n👋 Enter hi to start."
        record_text = "✅ 您的小确幸正准备发送至 Rum 种子网络"
        if type(text) == str and text.lower() in ["hi", "hello", "你好", "订阅"]:
            return welcome_text, None
        if type(text) == str and text.startswith("记录："):
            return record_text, None

        try:
            _num = int(text)
        except:
            return common_text, None

        if text not in list(commands.keys()):
            return common_text, None

        irss = {}
        # if text =="0":
        #    reply_text = f"👌 Ok，您仅订阅与自己的动态。{rum_adds}"
        if text == "1":
            reply_text = f"👌 Ok，您已订阅所有动态。{rum_adds}"
            irss[my_rum_group] = True
        elif text == "-1":
            reply_text = f"👌 Ok，您已关闭所有动态。{rum_adds}"
            irss[my_rum_group] = False
        else:
            return common_text, text

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
                    "is_rss": True,
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
        is_to_rum = len(msgview.data_decoded) > 7 and msgview.data_decoded.startswith("记录：")
        if is_to_rum:
            self.db.session.query(BotComments).filter(BotComments.message_id == msgview.message_id).update(
                {"is_reply": True, "is_to_rum": False}
            )
            self.db.commit()
        return is_to_rum

    def counts_trxs(self, days=-1, num=100):

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

    def airdrop_to_bot(self, memo=None, asset="rum"):
        _today = str(datetime.datetime.now().date())
        memo = memo or f"{_today} 与小确幸相伴"
        users = self.db.session.query(distinct(BotRss.user_id)).all()

        _amout = assets_info[asset]["amout"]
        _father = int(1 / _amout)
        for user in users:
            if len(users) < 1:
                continue
            user = user[0]
            sent = (
                self.db.session.query(BotAirDrops)
                .filter(and_(BotAirDrops.mixin_id == user, BotAirDrops.memo == memo))
                .first()
            )
            if sent:  # 用钱包排重，不重复空投
                continue

            _num = str(round(_amout + random.randint(1, 300) / (_father * _father), 6))
            r = self.xin.api.transfer.send_to_user(user, assets_info[asset]["id"], _num, memo)
            _a = {"mixin_id": user, "num": _num, "token": assets_info[asset]["symbol"], "memo": memo, "is_sent": False}
            if "data" in r:
                print(user, _num, "账户余额：", r.get("data").get("closing_balance"))
                _a["is_sent"] = True

            self.db.add(BotAirDrops(_a))


bot = LuckyBot()
