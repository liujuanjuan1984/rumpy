import os
import datetime

################ Rum ################
# quorum_client_port
rum_port = 58356

basedir = r"D:\Jupyter"
# git clone https://github.com/liujuanjuan1984/mixin-sdk-python
mixin_sdk_dirpath = os.path.join(basedir, "mixin-sdk-python")
rss_data_dir = os.path.join(basedir, "rss_rum_to_xin_data")


################ token ################
rum_asset_id = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"

################ xin ################

my_conversation_id = "e81c28a6-47aa-3aa0-97d2-62ac1754c90f"
my_user_id = "bae95683-eabb-422f-9588-24dadffd0323"
my_rum_group = "4e784292-6a65-471e-9f80-e91202e3358c"

################ files data ################

# files_to_records_data

mixin_bot_config_file = os.path.join(rss_data_dir, "bot-keystore.json")
# rss_file = os.path.join(rss_data_dir, "rss.json")
# trxs_file = os.path.join(rss_data_dir, "rum_trxs_to_post.json")
# bot_comments_file = os.path.join(rss_data_dir, "bot_comments.json")
# note_file = os.path.join(rss_data_dir, "notes_sent_to_rum.txt")  # 代发
# send_to_rum_file = os.path.join(rss_data_dir, "notes_sent_to_rum.json")  # 代发

# minutes: 最近小段时间内的内容才会被推送
commands = {
    "0": {"text": "取消所有订阅", "group_id": None},
    "1": {
        "text": "订阅 去中心微博",
        "group_id": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "minutes": -15,
    },
    "2": {
        "text": "订阅 Huoju在Rum上说了啥",
        "group_id": "f1bcdebd-4f1d-43b9-89d0-88d5fc896660",
        "minutes": -60,
    },
    "3": {
        "text": "订阅 去中心推特",
        "group_id": "bd119dd3-081b-4db6-9d9b-e19e3d6b387e",
        "minutes": -15,
    },
    "4": {
        "text": "订阅 RUM流动池与汇率",
        "group_id": "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436",
        "minutes": -15,
    },
    "5": {
        "text": "订阅 MOB流动池与汇率",
        "group_id": "dd90f5ec-2f63-4cff-b838-91695fe9150f",
        "minutes": -15,
    },
    "10": {
        "text": "订阅 刘娟娟的朋友圈",
        "group_id": "4e784292-6a65-471e-9f80-e91202e3358c",
        "minutes": -15,
    },
    "11": {
        "text": "订阅 杰克深的朋友圈",
        "group_id": "cfb42114-0ee1-429b-86e5-7659108972be",
        "minutes": -15,
    },
    "12": {
        "text": "订阅 老子到处说",
        "group_id": "c2ed5dff-321b-4020-a80e-f3f2e70cc2a1",
        "minutes": -15,
    },
    "20": {
        "text": "订阅 每天一分钟，知晓天下事",
        "group_id": "a6aac332-7c8d-4632-bf3c-725368bb89d5",
        "minutes": -60,
    },
    "99": {"text": "订阅以上所有", "group_id": -1},
}


rum_adds = "\n👨‍👩‍👧‍👦 获取最佳用户体验，安装 Rum Apps 🥂: https://rumsystem.net/apps\n"


welcome_text = "👋 hello 输入数字，订阅相应的种子网络" + (
    "\n🤖 输入数字的负数，取消订阅该种子网络，比如 10 的负数是 -10\n\n"
    + "\n".join([key + " " + commands[key]["text"] for key in commands])
    + "\n"
    + rum_adds
    + "\n有任何疑问或建议，请私聊刘娟娟\n\n最近更新：升级了订阅器的数据读写，从 file 改为 database，您之前的订阅数据已重置，请您重新订阅。\n为测试升级后的 bot 表现是否稳定，5月14日至21日，每天至少一波小额 RUM token 空投。"
)
