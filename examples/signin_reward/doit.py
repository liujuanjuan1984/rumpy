import datetime
import sys

# git clone https://github.com/liujuanjuan1984/mixin-sdk-python
mixin_dirpath = r"D:\Jupyter\mixin-sdk-python"
sys.path.insert(0, mixin_dirpath)
import mixinsdk
from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from examples._example_vars import BOT_CONFIG_FILE, CNB_ASSET_ID, MY_USER_ID


def get_rewards():
    from rumit import Rumit

    rum = Rumit(port=58356)
    rum.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"  # 刘娟娟的朋友圈
    # rum.group_id = '3bb7a3be-d145-44af-94cf-e64b992ff8f0' # 去中心微博
    to_rewards = rum.rewards(days=-2)
    print(to_rewards)
    return to_rewards


to_rewards = {
    "group_id": "4e784292-6a65-471e-9f80-e91202e3358c",
    "date": "2022-05-07",
    "data": {
        "bae95683-eabb-422f-9588-24dadffd0323": {
            "pubkey": "CAISIQNKNsvS2jHrqPqQZoHfShqu9P7a81glEa/A2WUVFtwRBQ==",
            "wallet": "bae95683-eabb-422f-9588-24dadffd0323",
            "name": "编程自由",
            "num": 20,
        },
    },
}

xin = HttpClient_BotAuth(BotConfig.from_file(BOT_CONFIG_FILE))


def send_reward(to_userid, name, asset, num, memo):
    r = xin.api.transfer.send_to_user(to_userid, asset, str(num), memo)
    print("账户余额", r.get("data").get("closing_balance"))


rum_asset_id = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"
for to_userid in to_rewards["data"]:
    name = to_rewards["data"][to_userid]["name"]
    d = to_rewards["date"]
    send_reward(to_userid, name, rum_asset_id, "0.00001", f"[debug]Rum 种子网络“刘娟娟的朋友圈” {d} 空投奖励")
