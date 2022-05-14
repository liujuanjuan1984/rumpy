import datetime
import sys
from config_rss import *

sys.path.insert(0, mixin_sdk_dirpath)

from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.types.message import MessageView, pack_message, pack_text_data
from modules import BotComments
from bot import bot


def message_handle_error_callback(error, details):
    print(datetime.datetime.now(), "===== error_callback =====")
    print(f"error: {error}")
    print(f"details: {details}")
    print(datetime.datetime.now(), "-" * 80)


async def message_handle(message):
    global bot
    global rss
    global bot_comments

    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        print(datetime.datetime.now(), "Mixin blaze server: received the message")
        return

    if action == "LIST_PENDING_MESSAGES":
        print(datetime.datetime.now(), "Mixin blaze server: list pending message")
        return

    if action == "ERROR":
        print(datetime.datetime.now(), message["error"])
        return

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        print(datetime.datetime.now(), error)
        return

    msgview = MessageView.from_dict(message["data"])

    # 和 server 有 -8 时差。也就是只处理 1 小时内的 message
    if msgview.created_at <= datetime.datetime.now() + datetime.timedelta(hours=-9):
        await bot.blaze.echo(msgview.message_id)
        return

    if msgview.type != "message":
        return

    if msgview.conversation_id in ("", None):
        return

    if msgview.data_decoded in ("", None):
        return

    # record the message
    # 查询 bot_comments
    print(datetime.datetime.now(), str(msgview.created_at), msgview.user_id)

    existed = bot.db.session.query(BotComments).filter(BotComments.message_id == msgview.message_id).first()
    # 消息没有计入数据库，就写入
    if existed == None:
        if bot.to_send_to_rum(msgview):
            await bot.blaze.echo(msgview.message_id)
            return
    # 已经响应过的，就不再回复
    elif existed.is_reply == True:
        await bot.blaze.echo(msgview.message_id)
        return

    reply_text, irss = bot.get_reply_text(msgview.data_decoded)
    bot.update_rss(msgview.user_id, irss)

    # send reply
    msg = pack_message(
        pack_text_data(reply_text), conversation_id=msgview.conversation_id, quote_message_id=msgview.message_id
    )
    bot.xin.api.send_messages(msg)
    await bot.blaze.echo(msgview.message_id)
    bot.db.session.query(BotComments).filter(BotComments.message_id == msgview.message_id).update({"is_reply": True})
    bot.db.commit()
    return


bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
)


bot.blaze.run_forever(2)
