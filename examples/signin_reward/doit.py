import datetime
import sys
import os
import random
from officy import JsonFile
from config_dev import rum_port, rum_asset_id, mixin_sdk_dirpath, mixin_bot_config_file
from rumit import Rumit

sys.path.insert(0, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth

rum = Rumit(port=rum_port)
xin = HttpClient_BotAuth(BotConfig.from_file(mixin_bot_config_file))
num_trxs = 1
days = -1


def reward_by_group(group_id):
    rum.group_id = group_id
    group_name = rum.group.seed()["group_name"]
    to_rewards = rum.rewards(n=num_trxs, days=days)
    date = to_rewards["date"]
    print(datetime.datetime.now(), group_id, group_name, "...")

    group_data = {"group_id": group_id, "group_name": group_name, "date": date, "to_rewards": to_rewards}

    for to_userid in to_rewards["data"]:
        name = to_rewards["data"][to_userid]["name"]
        _num = str(round(0.001 + random.randint(1, 100) / 1000000, 6))
        r = xin.api.transfer.send_to_user(to_userid, rum_asset_id, _num, f"[{date}]Rum 种子网络“{group_name}” 空投")
        print(to_userid, str(_num), name, "balance:", r.get("data").get("closing_balance"))
        to_rewards["data"][to_userid]["rum"] = _num

    group_data["to_rewards"] = to_rewards
    return group_data


def reward_by_node():
    all_data = {}
    for group_id in rum.node.groups_id:
        all_data[group_id] = reward_by_group(group_id)
    return all_data


def main():
    date = str(datetime.datetime.now().date() + datetime.timedelta(days=days))
    datafile = os.path.join(os.path.dirname(__file__), "data", f"{date}_rewards_all.json")
    if os.path.exists(datafile):
        return print(datetime.datetime.now(), "file exists. rewards is done.", datafile)

    data = reward_by_node()
    # data = reward_by_node(group_id="4e784292-6a65-471e-9f80-e91202e3358c") #刘娟娟的朋友圈
    JsonFile(datafile).write(data)


if __name__ == "__main__":
    main()
