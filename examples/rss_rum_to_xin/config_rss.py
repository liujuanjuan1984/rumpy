import os

DB_NAME = f"sqlite:///rss_bot_test.db"
################ Rum ################
# quorum_client_port
RUM_PORT = 62663

basedir = r"C:\Jupyter"
# git clone https://github.com/liujuanjuan1984/mixin-sdk-python
RUMPY_PATH = os.path.join(basedir, "rumpy")
MIXIN_SDK_PATH = os.path.join(basedir, "mixin-sdk-python")
rss_data_dir = os.path.join(basedir, "rss_rum_to_xin_data")
MIXIN_KEYSTORE_FILE = os.path.join(rss_data_dir, "bot-keystore.json")

RUM_ASSET_ID = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"
MY_CONVERSATION_ID = "e81c28a6-47aa-3aa0-97d2-62ac1754c90f"
MY_XIN_USER_ID = "bae95683-eabb-422f-9588-24dadffd0323"
MY_RUM_GROUP_ID = "4e784292-6a65-471e-9f80-e91202e3358c"


DEFAULT_MINUTES = -60
RUM_REWARD_BASE_NUM = 0.001

RSS_BOT_COMMANDS = {
    "0": {"text": "取消所有订阅", "group_id": None},
    "1": {
        "text": "订阅 去中心微博",
        "group_id": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "minutes": DEFAULT_MINUTES,
    },
    "2": {
        "text": "订阅 Huoju在Rum上说了啥",
        "group_id": "f1bcdebd-4f1d-43b9-89d0-88d5fc896660",
        "minutes": DEFAULT_MINUTES,
    },
    "3": {
        "text": "订阅 去中心推特",
        "group_id": "bd119dd3-081b-4db6-9d9b-e19e3d6b387e",
        "minutes": DEFAULT_MINUTES,
    },
    "4": {
        "text": "订阅 RUM流动池与汇率",
        "group_id": "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436",
        "minutes": int(DEFAULT_MINUTES * 0.25),
    },
    "5": {
        "text": "订阅 MOB流动池与汇率",
        "group_id": "dd90f5ec-2f63-4cff-b838-91695fe9150f",
        "minutes": int(DEFAULT_MINUTES * 0.25),
    },
    "10": {
        "text": "订阅 刘娟娟的朋友圈",
        "group_id": "4e784292-6a65-471e-9f80-e91202e3358c",
        "minutes": DEFAULT_MINUTES,
    },
    "11": {
        "text": "订阅 杰克深的朋友圈",
        "group_id": "cfb42114-0ee1-429b-86e5-7659108972be",
        "minutes": DEFAULT_MINUTES,
    },
    "12": {
        "text": "订阅 老子到处说",
        "group_id": "c2ed5dff-321b-4020-a80e-f3f2e70cc2a1",
        "minutes": DEFAULT_MINUTES,
    },
    "20": {
        "text": "订阅 每天一分钟，知晓天下事",
        "group_id": "a6aac332-7c8d-4632-bf3c-725368bb89d5",
        "minutes": DEFAULT_MINUTES,
    },
    "99": {"text": "订阅以上所有", "group_id": -1},
}


ADDS_TEXT = "\n👨‍👩‍👧‍👦 获取最佳用户体验，安装 Rum Apps 🥂: https://rumsystem.net/apps\n"


WELCOME_TEXT = "👋 hello 输入数字，订阅相应的种子网络" + (
    "\n🤖 输入数字的负数，取消订阅该种子网络，比如 10 的负数是 -10\n\n"
    + "\n".join([key + " " + RSS_BOT_COMMANDS[key]["text"] for key in RSS_BOT_COMMANDS])
    + "\n"
    + ADDS_TEXT
    + "\n如果您长时间未能收到任何动态，请反馈刘娟娟，或重新订阅。\n\n新增小工具：输入你的生日，比如“生日 1990 1 24”，将得到你这一辈子的数据（七年就是一辈子）。"
)
