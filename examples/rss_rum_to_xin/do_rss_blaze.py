# Application case https://github.com/infowoods/oogway-mixin-bot

import asyncio
import time
import datetime
import sys
from officy import JsonFile
from config_dev import mixin_sdk_dirpath
from config_rss import *

sys.path.insert(0, mixin_sdk_dirpath)

from mixinsdk.clients.bot_config import BotConfig
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_BotAuth
from mixinsdk.types.message import MessageView, pack_text_data, pack_message


# read data
rum_groups_to_view = JsonFile(rum_groups_to_view_file).read({})
rss = JsonFile(rss_file).read({})
bot_comments = JsonFile(bot_comments_file).read({})


class MixinBotClient:
    def __init__(self):
        self.blaze: BlazeClient = None
        self.http: HttpClient_BotAuth = None


def message_handle_error_callback(error, details):
    print("===== error_callback =====")
    print(f"error: {error}")
    print(f"details: {details}")
    print("-" * 80)


async def message_handle(message):
    global bot
    global rss
    global bot_comments

    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # mixin blaze server received the message
        return

    if action == "LIST_PENDING_MESSAGES":
        print("Mixin blaze server: 👂")
        return

    if action == "ERROR":
        print(message["error"])
        return

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        print(error)
        return

    msgview = MessageView.from_dict(message["data"])
    msg_cid = msgview.conversation_id
    if msg_cid == "":
        # is response status of send message, ignore
        return

    msg_text = msgview.data_decoded

    if msg_text == "":
        # is response status of send message, ignore
        return

    msg_id = msgview.message_id

    # record the message
    if msg_cid not in bot_comments:
        bot_comments[msg_cid] = {}
    if msg_id not in bot_comments[msg_cid]:
        bot_comments[msg_cid][msg_id] = {
            "message_id": msg_id,
            "text": msg_text,
            "is_replyed": False,
        }

    # check is_replyed
    if bot_comments[msg_cid][msg_id]["is_replyed"]:
        return

    if msgview.type != "message":
        return

    print(datetime.datetime.now(), f"message from: {msgview.user_id} {msg_text}")

    # help to send note to rum network
    if msg_cid == my_conversation_id and len(msg_text) > 10 and msg_text.startswith("代发："):
        to_sends = JsonFile(send_to_rum_file).read({})
        if msg_id not in to_sends:
            to_sends[msg_id] = {"text": msg_text[3:], "create_at": str(datetime.datetime.now())}
        JsonFile(send_to_rum_file).write(to_sends)
        bot_comments[msg_cid][msg_id]["is_replyed"] = str(datetime.datetime.now())
        JsonFile(bot_comments_file).write(bot_comments)
        return

    # get the reply_text
    try:
        int(msg_text)
        rss_flag = True
    except:
        rss_flag = False

    if not rss_flag:
        reply_text = welcome_text
    elif str(abs(int(msg_text))) in list(commands.keys()):
        _gidx = commands[str(abs(int(msg_text)))]["group_id"]
        if _gidx == None:  # 取消所有
            for _gid in rss:
                rss[_gid][msg_cid] = {}
            reply_text = f"👌 Ok，您已取消订阅所有种子网络。{rum_adds}"
        elif _gidx == -1:  # 订阅所有
            for _gid in rss:
                _gname = rum_groups_to_view[_gid]["group_name"]
                rss[_gid][msg_cid] = {
                    "conversation_id": msg_cid,
                    "user_id": msgview.user_id,
                }
            reply_text = f"✅ Yes，您已成功订阅所有种子网络。{rum_adds}"
        else:  # 修改订阅
            # 增加订阅
            _gname = rum_groups_to_view[_gidx]["group_name"]
            if int(msg_text) > 0:
                rss[_gidx][msg_cid] = {
                    "conversation_id": msg_cid,
                    "user_id": msgview.user_id,
                }
                reply_text = f"✅ Yes，您已成功订阅 {_gname}{rum_adds}"
            else:
                # 取消订阅
                rss[_gidx][msg_cid] = {}
                reply_text = f"👌 Ok，您已取消订阅{_gname}{rum_adds}"
    else:
        reply_text = welcome_text

    # send reply
    JsonFile(rss_file).write(rss)
    msg = pack_message(
        pack_text_data(reply_text),
        msg_cid,
    )

    bot.http.api.send_messages(msg)
    await bot.blaze.echo(msg_id)

    bot_comments[msg_cid][msg_id]["is_replyed"] = str(datetime.datetime.now())
    JsonFile(bot_comments_file).write(bot_comments)
    time.sleep(1)
    return


bot_config = BotConfig.from_file(mixin_bot_config_file)
bot = MixinBotClient()

bot.http = HttpClient_BotAuth(bot_config)
bot.blaze = BlazeClient(
    bot_config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
)


asyncio.run(bot.blaze.run_forever(2))
