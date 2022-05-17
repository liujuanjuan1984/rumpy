import os
import datetime

# quorum_client_port
rum_port = 58356

basedir = r"D:\Jupyter"
# git clone https://github.com/liujuanjuan1984/mixin-sdk-python
mixin_sdk_dirpath = os.path.join(basedir, "mixin-sdk-python")

rum_asset_id = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"
my_conversation_id = "e81c28a6-47aa-3aa0-97d2-62ac1754c90f"
my_user_id = "bae95683-eabb-422f-9588-24dadffd0323"
my_rum_group = "9940a277-a808-4e86-8fb1-48c2d072d1d7"
my_rum_group_name = "每天的小确幸"
mixin_bot_config_file = os.path.join(os.path.dirname(__file__), "keystore.json")


assets_info = {"rum": {"id": "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f", "symbol": "RUM", "amout": 0.001}}

default_minutes = -120


commands = {
    "0": {
        "text": "订阅仅与自己相关的动态",
        "group_id": my_rum_group,
        "minutes": default_minutes,
    },
    "1": {
        "text": "订阅所有动态",
        "group_id": my_rum_group,
        "minutes": default_minutes,
    },
    "-1": {
        "text": "关闭所有动态",
        "group_id": my_rum_group,
        "minutes": default_minutes,
    },
}


rum_adds = "\n👨‍👩‍👧‍👦 获取最佳用户体验，安装 Rum Apps 🥂: https://rumsystem.net/apps\n"


welcome_text = """👋 hello 欢迎加入我们，每天与小确幸相伴~

向该 bot 发送文本消息，并以“记录：”开头，比如“记录：我今天看到了彩虹，那是在下午三点钟...”，该 bot 将自动为您把该记录推送到 Rum 种子网络上链存储。

1 订阅所有动态
-1 关闭动态推送

该 bot 仍在开发中，欢迎体验。
"""
