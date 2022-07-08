import datetime
import json
import logging
import re
import sys
import time

from config_rss import *

from rumpy import FullNode

sys.path.insert(0, RUMPY_PATH)
sys.path.insert(0, MIXIN_SDK_PATH)
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data
from modules import *
from seven_years_circle import SevenYearsCircle
from sqlalchemy import Boolean, Column, Integer, String, and_, distinct

now = datetime.datetime.now()

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    filename=f"rss_blaze_{datetime.date.today()}_{now.hour}_{now.minute}.log",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


class BlazeBot:
    def __init__(self, db_name=None):
        self.config = AppConfig.from_file(MIXIN_KEYSTORE_FILE)
        self.db = BaseDB(db_name or DB_NAME, echo=False, reset=False)
        self.rum = FullNode(port=RUM_PORT)
        self.groups = self.check_groups()

    def check_groups(self):
        groups = {}
        for k in RSS_BOT_COMMANDS:
            _gid = RSS_BOT_COMMANDS[k]["group_id"]
            if _gid not in (None, -1):
                self.rum.group_id = _gid
                groups[_gid] = {
                    "group_id": _gid,
                    "group_name": self.rum.api.seed().get("group_name"),
                    "minutes": RSS_BOT_COMMANDS[k].get("minutes") or DEFAULT_MINUTES,
                }
        return groups

    def check_str_param(self, text):
        if type(text) == str:
            return text
        if type(text) == dict:
            return json.dumps(text)
        return str(text)

    def to_send_to_rum(self, msgview, db_session):
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

        db_session.add(BotComments(_c))
        is_to_rum = (
            msgview.conversation_id == MY_CONVERSATION_ID
            and len(msgview.data_decoded) > 10
            and msgview.data_decoded.startswith("代发")
        )
        if is_to_rum:

            db_session.query(BotComments).filter(BotComments.message_id == msgview.message_id).update(
                {"is_reply": True, "is_to_rum": False}
            )
            db_session.commit()
        logger.debug(f"need to_send_to_rum? {is_to_rum}, message_id: {msgview.message_id}")
        return is_to_rum

    def get_reply_text(self, text):
        if type(text) == str and text.lower() in ["hi", "hello", "你好", "订阅"]:
            return WELCOME_TEXT, None

        if type(text) == str and text.startswith("生日"):
            reply_text = (
                "请按如下格式输入，以“生日”开头，“年月日”的数字之间要用空格或其它标点符号分开。以下写法都是支持的：\n生日 1990 1 24\n生日，2001。12。24\n生日1972 7 12\n"
            )
            rlts = re.findall(r"^生日\D*?(\d{4})\D*?(\d{1,2})\D*?(\d{1,2})\D*?$", text)
            if rlts:
                try:
                    reply_text = SevenYearsCircle(*rlts[0]).text_status()
                except:
                    pass
            return reply_text, None

        try:
            _num = int(text)
            _abs = abs(_num)
        except:
            return "输入 hi 查看操作说明", None

        if str(_abs) not in list(RSS_BOT_COMMANDS.keys()):
            return "输入 hi 查看操作说明", None

        irss = {}  # init
        for group_id in self.groups:
            irss[group_id] = None

        _gidx = RSS_BOT_COMMANDS[str(_abs)]["group_id"]
        if _gidx == None:  # 取消所有
            for _gid in irss:
                irss[_gid] = False
            reply_text = f"👌 Ok，您已取消订阅所有种子网络。{ADDS_TEXT}"
        elif _gidx == -1:  # 订阅所有
            for _gid in irss:
                irss[_gid] = True
            reply_text = f"✅ Yes，您已成功订阅所有种子网络。{ADDS_TEXT}"
        else:
            # 修改订阅：增加或推定
            _gname = RSS_BOT_COMMANDS[str(_abs)]["text"]
            if _num > 0:
                irss[_gidx] = True
                reply_text = f"✅ Yes，您已成功{_gname}{ADDS_TEXT}"
            else:
                # 取消订阅
                irss[_gidx] = False
                reply_text = f"👌 Ok，您已取消{_gname}{ADDS_TEXT}"
        return reply_text, irss

    def update_rss(self, user_id, irss, db_session, xin_http_session):
        if irss is None:
            return
        for group_id in irss:
            ug = user_id + group_id
            existd = db_session.query(BotRss).filter(BotRss.user_group == ug).first()
            if existd:
                if irss[group_id] != None and existd.is_rss != irss[group_id]:
                    db_session.query(BotRss).filter(BotRss.user_group == ug).update({"is_rss": irss[group_id]})
                    db_session.commit()
                logger.debug(f"update rss, user_id: {user_id}, group_id: {group_id}, is_rss: {irss[group_id]}")
            else:
                data = {
                    "user_id": user_id,
                    "group_id": group_id,
                    "is_rss": irss[group_id],
                    "user_group": ug,
                    "conversation_id": xin_http_session.get_conversation_id_with_user(user_id),
                }
                db_session.add(BotRss(data))
                logger.debug(f"add rss, user_id: {user_id}, group_id: {group_id}, is_rss: {irss[group_id]}")


def message_handle_error_callback(error, details):
    logger.error("===== error_callback =====")
    logger.error(f"error: {error}")
    logger.error(f"details: {details}")


async def message_handle(message):
    global bot
    db_session = bot.db.Session()
    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # logger.info("Mixin blaze server: received the message")
        return

    if action == "LIST_PENDING_MESSAGES":
        # logger.info("Mixin blaze server: list pending message")
        return

    if action == "ERROR":
        logger.warning(message["error"])
        await bot.blaze.echo(msgview.message_id)
        return

    if action != "CREATE_MESSAGE":
        await bot.blaze.echo(msgview.message_id)
        return

    error = message.get("error")
    if error:
        logger.info(str(error))
        await bot.blaze.echo(msgview.message_id)
        return

    msgview = MessageView.from_dict(message["data"])

    # 和 server 有 -8 时差。也就是只处理 1 小时内的 message
    if msgview.created_at <= datetime.datetime.now() + datetime.timedelta(hours=-9):
        await bot.blaze.echo(msgview.message_id)
        return

    if msgview.type != "message":
        await bot.blaze.echo(msgview.message_id)
        return

    if msgview.conversation_id in ("", None):
        await bot.blaze.echo(msgview.message_id)
        return

    if msgview.data_decoded in ("", None):
        await bot.blaze.echo(msgview.message_id)
        return

    if type(msgview.data_decoded) != str:
        await bot.blaze.echo(msgview.message_id)
        return
    # record the message
    # 查询 bot_comments

    logger.info(
        f"msgview {str(msgview.created_at+datetime.timedelta(hours=8))}, user_id: {msgview.user_id}, message_id {msgview.message_id}"
    )

    existed = db_session.query(BotComments).filter(BotComments.message_id == msgview.message_id).first()
    # 消息没有计入数据库，就写入
    if existed == None:
        logger.debug(f"not existed in db. message_id {msgview.message_id}")
        if bot.to_send_to_rum(msgview, db_session=db_session):
            await bot.blaze.echo(msgview.message_id)
            return
    # 已经响应过的，就不再回复
    else:
        logger.debug(f"existed in db. message_id {msgview.message_id}. is_reply:{existed.is_reply}")
        if existed.is_reply == True:
            await bot.blaze.echo(msgview.message_id)
            return

    reply_text, irss = bot.get_reply_text(msgview.data_decoded)
    bot.update_rss(msgview.user_id, irss, db_session=db_session, xin_http_session=bot.xin)

    # send reply

    msg = pack_message(
        pack_text_data(reply_text),
        conversation_id=msgview.conversation_id,
        quote_message_id=msgview.message_id,
    )
    logger.debug(f"pack_message {msgview.message_id} {reply_text}")
    resp = bot.xin.api.send_messages(msg)
    logger.debug(f"pack_message resp??? {json.dumps(resp)}")

    if "data" in resp:
        logger.info(f"bot.xin.api.send_messages success. message_id: {msgview.message_id}")
        await bot.blaze.echo(msgview.message_id)
        db_session.query(BotComments).filter(BotComments.message_id == msgview.message_id).update({"is_reply": True})
        db_session.commit()
        logger.info(f"bot.xin.api.send_messages success to db. message_id: {msgview.message_id}")
    else:
        logger.info(f"xin.api.send_messages {json.dumps(resp)}")
    return


bot = BlazeBot()
bot.xin = HttpClient_AppAuth(bot.config)
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
)


bot.blaze.run_forever(2)
