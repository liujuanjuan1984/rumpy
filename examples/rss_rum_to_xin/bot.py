import datetime
import logging

now = datetime.datetime.now()

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    filename=f"rss_{datetime.date.today()}_{now.hour}_{now.minute}.log",
    level=logging.INFO,
)


import datetime
import json
import logging
import os
import random
import sys
import time

from config_rss import *
from modules import *
from sqlalchemy import Boolean, Column, Integer, String, and_, distinct

import rumpy
import rumpy.utils as utils
from rumpy import FullNode

sys.path.insert(0, MIXIN_SDK_PATH)
import mixinsdk
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data

logger = logging.getLogger(__name__)

"""
rss bot 是一个基于 mixin messenger 的 bot
本模块的功能是从 rum 网络获取待转发的数据，并根据用户与 rss bot 所发出的订阅要求，转发到 xin
"""


class RssBot:
    def __init__(self, db_name=None):
        self.rum = FullNode(port=RUM_PORT)
        self.config = AppConfig.from_file(MIXIN_KEYSTORE_FILE)
        self.xin = HttpClient_AppAuth(self.config)
        self.db = BaseDB(db_name or DB_NAME, echo=False, reset=False)
        self.groups = self.check_groups()
        self.update_all_profiles("bot")

    def update_profiles(self, group_id):
        _x = and_(
            BotRumProgress.group_id == group_id,
            BotRumProgress.progress_type == "GET_PROFILES",
        )
        progress = self.db.session.query(BotRumProgress).filter(_x).first()

        if progress == None:
            _p = {
                "progress_type": "GET_PROFILES",
                "trx_id": None,
                "timestamp": None,
                "group_id": group_id,
            }
            self.db.add(BotRumProgress(_p))

        p_tid = None if progress == None else progress.trx_id

        users_data = self.rum.api.update_profiles_data(
            group_id=group_id,
            users_data={"trx_id": p_tid},
            types=("name", "wallet"),
        )
        if users_data is None:
            return
        tid = users_data.get("trx_id")
        ts = users_data.get("trx_timestamp")

        if tid and tid != p_tid:
            self.db.session.query(BotRumProgress).filter(_x).update({"trx_id": tid, "timestamp": ts})
            self.db.session.commit()

        users = users_data.get("data", {})
        for pubkey in users:
            if pubkey == "progress_tid":
                continue
            _name = users[pubkey].get("name", pubkey)
            _wallet = users[pubkey].get("wallet", None)
            if type(_wallet) == list:
                _wallet = _wallet[0]["id"]
            _x = and_(
                BotRumProfiles.group_id == group_id,
                BotRumProfiles.pubkey == pubkey,
            )
            existd = self.db.session.query(BotRumProfiles).filter(_x).first()
            if not existd:
                _p = {
                    "group_id": group_id,
                    "pubkey": pubkey,
                    "name": _name,
                    "wallet": _wallet,
                    "timestamp": ts,
                }
                self.db.add(BotRumProfiles(_p))
            elif existd.timestamp < ts:
                _p = {"timestamp": ts}
                if _name != existd.name:
                    _p["name"] = _name
                if _wallet != existd.wallet:
                    _p["wallet"] = _wallet

                self.db.session.query(BotRumProfiles).filter(_x).update(_p)
                self.db.commit()

    def update_all_profiles(self, where="bot"):
        groups = []
        if where == "bot":
            groups = self.groups
        elif where == "node":
            groups = self.rum.api.groups_id

        for group_id in groups:
            self.update_profiles(group_id)

    def check_groups(self):
        groups = {}
        for k in RSS_BOT_COMMANDS:
            _gid = RSS_BOT_COMMANDS[k]["group_id"]
            if _gid not in (None, -1):
                groups[_gid] = {
                    "group_id": _gid,
                    "group_name": utils.group_name(self.rum.api.seed(_gid)["seed"]),
                    "minutes": RSS_BOT_COMMANDS[k].get("minutes") or DEFAULT_MINUTES,
                }
        return groups

    def get_nicknames(self, group_id):
        _nn = self.db.session.query(BotRumProfiles).filter(BotRumProfiles.group_id == group_id).all()
        nicknames = {}
        for _n in _nn:
            nicknames[_n.pubkey] = {"name": _n.name}
        return nicknames

    def get_trxs_from_rum(self):
        for group_id in self.groups:
            if not self.rum.api.is_joined(group_id):
                logger.warning(f"group_id: {group_id}, you are not in this group. you need to join it.")
                continue

            nicknames = self.get_nicknames(group_id)
            existd = (
                self.db.session.query(BotRumProgress)
                .filter(
                    and_(
                        BotRumProgress.group_id == group_id,
                        BotRumProgress.progress_type == "GET_CONTENT",
                    )
                )
                .first()
            )

            gname = self.groups[group_id]["group_name"]
            minutes = self.groups[group_id]["minutes"]
            if not existd:
                _trxs = self.rum.api.get_group_content(group_id=group_id, reverse=True, num=10)
                if len(_trxs) > 0:
                    trx_id = _trxs[-1]["TrxId"]
                    _ts = str(utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]))
                else:
                    trx_id = None
                    _ts = None

                _p = {
                    "progress_type": "GET_CONTENT",
                    "trx_id": trx_id,
                    "timestamp": _ts,
                    "group_id": group_id,
                }
                self.db.add(BotRumProgress(_p))
            else:
                trx_id = existd.trx_id

            trxs = self.rum.api.get_group_content(group_id=group_id, trx_id=trx_id, num=10)
            for trx in trxs:
                _tid = trx["TrxId"]
                trx_id = _tid
                self.db.session.query(BotRumProgress).filter(
                    and_(
                        BotRumProgress.group_id == group_id,
                        BotRumProgress.progress_type == "GET_CONTENT",
                    )
                ).update({"trx_id": trx_id})
                self.db.commit()
                existd2 = self.db.session.query(BotTrxs).filter(BotTrxs.trx_id == _tid).first()
                if existd2:
                    continue

                ts = str(utils.timestamp_to_datetime(trx["TimeStamp"]))  # 只发距今xx小时的更新，间隔时间由配置文件控制
                if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=minutes)):
                    continue

                obj = self.rum.api.trx_retweet_params(group_id=group_id, trx=trx)
                if not obj:
                    continue

                pubkey = trx["Publisher"]
                if pubkey not in nicknames:
                    username = pubkey[-10:-2]
                else:
                    username = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})" or pubkey[-10:-2]
                obj["content"] = f"{username}@{gname}\n{obj['content']}"

                _trx = {
                    "trx_id": _tid,
                    "group_id": group_id,
                    "timestamp": ts,
                    "text": obj["content"].encode().decode("utf-8"),
                }
                logger.info(f"got new trx from rum. trx_id: {_tid}, group_id: {group_id}")
                self.db.add(BotTrxs(_trx))

    def send_msg_to_xin_update(self):
        # 先筛选出等待推送的 trxs，再推送给订阅了的人。

        # 计算出时间
        def _get_nice_ts(group_id):
            nice_ts = str(datetime.datetime.now() + datetime.timedelta(minutes=self.groups[group_id]["minutes"]))
            return nice_ts

        def _check_text(text):
            # subs = (" 点赞给 `"," 点踩给 `"," 修改了个人信息：","OBJECT_STATUS_DELETED")
            # is_pass = utils.check_sub_strs(text,*subs)
            # if is_pass and not is_except:
            #    return False

            sub = "Happyness(hDZVqRpg)@Huoju在Rum上说了啥"
            is_except = utils.check_sub_strs(text, sub)

            subs = (" 点赞给 `", " 点踩给 `")
            is_split = utils.check_sub_strs(text, *subs)
            if is_split and not is_except:
                text = text.split("所发布的内容：")[0] + "所发布的内容。"

            # 移除种子来源展示
            if is_except:
                text = text.split("origin: ")[0]

            _length = 200
            if len(text) > _length:
                text = text[:_length] + "...略..."
            return text

        def _one_group(group_id):
            nice_ts = _get_nice_ts(group_id)
            # 获取待发的 trxs
            trxs = (
                self.db.session.query(BotTrxs)
                .filter(
                    and_(
                        BotTrxs.group_id == group_id,
                        BotTrxs.timestamp > nice_ts,
                    )
                )
                .all()
            )
            # 筛选出待发的人
            users = (
                self.db.session.query(BotRss.user_id)
                .filter(and_(BotRss.is_rss == True, BotRss.group_id == group_id))
                .all()
            )
            for trx in trxs:
                logger.debug(f"trxs, trx_id:{trx.trx_id}")

                sent_users = (
                    self.db.session.query(BotTrxsSent.user_id)
                    .filter(
                        and_(
                            BotTrxsSent.trx_id == trx.trx_id,
                            BotTrxsSent.group_id == group_id,
                        )
                    )
                    .all()
                )
                _sent_users = [i[0] for i in sent_users]
                text = _check_text(trx.text)

                if text == False:
                    if MY_XIN_USER_ID in _sent_users:
                        continue

                    msg = pack_message(pack_text_data(trx.text), MY_CONVERSATION_ID)
                    logger.info(f"pack_message to myself, trx_id: {trx.trx_id}")
                    resp = self.xin.api.send_messages(msg)
                    logger.debug(f"send_messages to myself, trx_id: {trx.trx_id}")
                    if "data" in resp:
                        _d = {
                            "trx_id": trx.trx_id,
                            "group_id": group_id,
                            "user_id": MY_XIN_USER_ID,
                            "conversation_id": MY_CONVERSATION_ID,
                            "is_sent": True,
                        }
                        self.db.add(BotTrxsSent(_d))
                    else:
                        logger.debug(f"xin.api.send_messages resp: {json.dumps(resp)}")
                else:
                    # TODO:用 unpacking 的方式取代下标的方式；但要验证下
                    for user, *others in users:
                        logger.debug(f"user: {user}")
                        if user in _sent_users:
                            logger.debug(f"user in sent_users,user: {user},trx_id: {trx.trx_id}")
                            continue
                        cid = self.xin.get_conversation_id_with_user(user)
                        logger.debug(f"user not in sent_users,user: {user}, trx_id: {trx.trx_id}")
                        msg = pack_message(pack_text_data(trx.text), cid)
                        logger.info(f"pack_message,user: {user}, trx_id: {trx.trx_id}")
                        resp = self.xin.api.send_messages(msg)
                        logger.debug(f"send_messages,user: {user}, trx_id: {trx.trx_id}")

                        if "data" in resp:
                            _d = {
                                "trx_id": trx.trx_id,
                                "group_id": group_id,
                                "user_id": user,
                                "conversation_id": cid,
                                "is_sent": True,
                            }
                            self.db.add(BotTrxsSent(_d))
                        else:
                            logger.info(f"xin.api.send_messages resp: {json.dumps(resp)}")

        for group_id in self.groups:
            logger.debug(f"send_msg_to_xin_update, group_id: {group_id}")
            _one_group(group_id)

    def send_to_rum(self):
        logger.info("send_to_rum start ...")
        data = (
            self.db.session.query(BotComments)
            .filter(
                and_(
                    BotComments.user_id == MY_XIN_USER_ID,
                    BotComments.text.like("代发%"),
                )
            )
            .all()
        )
        for r in data:
            if r.is_to_rum:
                continue
            if r.text.startswith(r"代发微博"):
                group_id = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"
                text = r.text[5:]
            else:
                group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
                text = r.text[3:]
            resp = self.rum.api.send_note(group_id=group_id, content=text)
            logger.info(f"rum.api.send_note, message_id: {r.message_id}...")
            if "trx_id" not in resp:
                logger.warning(f"rum.api.send_note, resp: {json.dumps(resp)}")
                continue
            self.db.session.query(BotComments).filter(BotComments.message_id == r.message_id).update(
                {"is_to_rum": True}
            )
            self.db.commit()
            logger.info(f"rum.api.send_note, success. message_id: {r.message_id}...")
        logger.info("send_to_rum done")

    def do_rss(self):
        self.send_to_rum()
        self.send_msg_to_xin_update()
        self.get_trxs_from_rum()

    def counts_trxs(self, group_id, days=-1, num=100):
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
        counts_result = {"data": {}, "date": str(thatday)}
        while True:
            _trxs = self.rum.api.get_group_content(reverse=True, num=num)
            if len(_trxs) == 0:
                return counts_result
            if num >= 1000:
                return counts_result
            lastest_day = utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]).date()
            if lastest_day < thatday:
                counts = {}
                for _trx in _trxs:
                    _day = utils.timestamp_to_datetime(_trx["TimeStamp"]).date()
                    if _day == thatday:
                        _pubkey = _trx["Publisher"]
                        if _pubkey not in counts:
                            counts[_pubkey] = 1
                        else:
                            counts[_pubkey] += 1
                else:
                    counts_result["data"] = counts
                break
            else:
                logger.info(f"counts_trxs num:{num}, lastest_day:{lastest_day} thatday:{thatday}")
                num += 100

        return counts_result

    def airdrop_to_group(self, group_id, num_trxs=1, days=-1, memo=None):
        group_name = utils.group_name(self.rum.api.seed(group_id)["seed"])
        logger.debug(f"airdrop_to_group {group_id}, {group_name}, ...")

        counts_result = self.counts_trxs(group_id, days=days)
        date = datetime.datetime.now().date() + datetime.timedelta(days=days)
        memo = memo or f"{date} Rum 种子网络空投"
        for pubkey in counts_result["data"]:
            # trxs 条数够了
            if counts_result["data"][pubkey] < num_trxs:
                continue

            existd = (
                self.db.session.query(BotRumProfiles)
                .filter(
                    and_(
                        BotRumProfiles.pubkey == pubkey,
                        BotRumProfiles.wallet != None,
                    )
                )
                .first()
            )

            if existd:  # 有钱包
                name = existd.name
                sent = (
                    self.db.session.query(BotAirDrops)
                    .filter(
                        and_(
                            BotAirDrops.mixin_id == existd.wallet,
                            BotAirDrops.memo == memo,
                        )
                    )
                    .first()
                )
                if sent:  # 用钱包排重，不重复空投
                    continue

                _num = str(
                    round(
                        RUM_REWARD_BASE_NUM + random.randint(1, 300) / 1000000,
                        6,
                    )
                )
                _a = {
                    "mixin_id": existd.wallet,
                    "group_id": group_id,
                    "pubkey": pubkey,
                    "num": _num,
                    "token": "RUM",
                    "memo": memo,
                    "is_sent": False,
                }
                r = self.xin.api.transfer.send_to_user(existd.wallet, RUM_ASSET_ID, _num, memo)

                if "data" in r:
                    logger.info(
                        f"""airdrop_to_group mixin_id: {existd.wallet}, num: {_num}, balance: {r.get("data").get("closing_balance") or '???'}"""
                    )
                    _a["is_sent"] = True

                self.db.add(BotAirDrops(_a))

    def airdrop_to_node(self, num_trxs=1, days=-1, memo=None):
        for group_id in self.rum.api.groups_id:
            self.airdrop_to_group(group_id, num_trxs, days)

    def airdrop_to_bot(self, memo=None):
        _today = str(datetime.datetime.now().date())
        memo = memo or f"{_today} Rum 订阅器空投"
        users = self.db.session.query(distinct(BotRss.user_id)).all()
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

            _num = str(round(RUM_REWARD_BASE_NUM + random.randint(1, 300) / 1000000, 6))
            r = self.xin.api.transfer.send_to_user(user, RUM_ASSET_ID, _num, memo)
            _a = {
                "mixin_id": user,
                "num": _num,
                "token": "RUM",
                "memo": memo,
                "is_sent": False,
            }
            if "data" in r:
                logger.info(
                    f"""airdrop_to_bot mixin_id: {user}, num: {_num}, balance: {r.get("data").get("closing_balance") or '???'}"""
                )
                _a["is_sent"] = True

            self.db.add(BotAirDrops(_a))


if __name__ == "__main__":
    bot = RssBot()

    print(datetime.datetime.now(), "rss start...")

    while True:
        try:
            bot.do_rss()
        except Exception as e:
            print(e)
        time.sleep(1)
