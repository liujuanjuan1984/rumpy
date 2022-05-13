import datetime
import sys
import os
import time
import random
from officy import JsonFile
from config_rss import *
from rumit import Rumit

sys.path.insert(0, mixin_sdk_dirpath)
from mixinsdk.clients.http_client import AppConfig, HttpClient_AppAuth

rum = Rumit(port=rum_port)
xin = HttpClient_AppAuth(AppConfig.from_file(mixin_bot_config_file))
num_trxs = 1
days = -1

done_text = """"""


def airdrop_to_group(group_id):
    rum.group_id = group_id
    group_name = rum.group.seed()["group_name"]
    to_rewards = rum.rewards(n=num_trxs, days=days)
    date = to_rewards["date"]
    print(datetime.datetime.now(), group_id, group_name, "...")

    group_data = {"group_id": group_id, "group_name": group_name, "date": date, "to_rewards": to_rewards}

    for to_userid in to_rewards["data"]:
        if to_userid in done_text:
            print(to_userid, "done.")
            continue
        name = to_rewards["data"][to_userid]["name"]
        _num = str(round(0.001 + random.randint(1, 100) / 1000000, 6))
        r = xin.api.transfer.send_to_user(to_userid, rum_asset_id, _num, f"{date} Rum 种子网络“{group_name}” 空投")
        print(to_userid, str(_num), name, "balance:", r.get("data").get("closing_balance"))
        to_rewards["data"][to_userid]["rum"] = _num

    group_data["to_rewards"] = to_rewards
    return group_data


def airdrop_to_node():
    all_data = {}
    for group_id in rum.node.groups_id:
        all_data[group_id] = airdrop_to_group(group_id)
    return all_data


def airdrop_to_xin_bot_users():
    rss = JsonFile(rss_file).read({})
    to_useids = []
    for gid in rss:
        for conversation_id in rss[gid]:
            to_userid = rss[gid][conversation_id].get("user_id") or ""
            if to_userid and to_userid not in to_useids:
                to_useids.append(to_userid)
    _today = str(datetime.datetime.now().date())
    for to_userid in to_useids:
        if to_userid in done_text:
            print(to_userid, "done.")
            continue
        _num = str(round(0.001 + random.randint(1, 100) / 1000000, 6))
        try:
            r = xin.api.transfer.send_to_user(to_userid, rum_asset_id, _num, f"{_today} Rum订阅器空投")
            print(to_userid, str(_num), "账户余额：", r.get("data").get("closing_balance"))
            time.sleep(1)
        except Exception as e:
            print(to_userid, e)
            time.sleep(5)


def main():
    date = str(datetime.datetime.now().date() + datetime.timedelta(days=days))
    datafile = os.path.join(os.path.dirname(__file__), "data", f"{date}_rewards.json")
    if os.path.exists(datafile):
        return print(datetime.datetime.now(), "file exists. rewards is done.", datafile)

    data = airdrop_to_node()
    # data = airdrop_to_group(group_id="4e784292-6a65-471e-9f80-e91202e3358c")  # 刘娟娟的朋友圈
    JsonFile(datafile).write(data)


if __name__ == "__main__":
    main()
    # airdrop_to_xin_bot_users()
