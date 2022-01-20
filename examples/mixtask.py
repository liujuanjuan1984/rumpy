"""把所有需要长期运行的任务，合并到一起，线性运行。"""
import os
import sys
import pandas as pd
from time import sleep
import datetime
import random

homedir = r"D:\Jupyter\rumpy"
sys.path.append(homedir)
from rumpy import RumClient, JsonFile, Dir
from examples.search_seeds.search_seeds import SearchSeeds
from examples.whosays.whosays import WhoSays
from examples.group_statistics.group_statistics import GroupStatistics

client_params = {
    "port": 59402,
    "crtfile": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",  # r"D:\RUM2-DATA\certs\server.crt",
}

client = RumClient(**client_params)
logsfile = homedir + r"\examples\logs.json"


def hans_count(str):
    hans_total = 0
    for s in str:
        # 中文字符其实还有很多，但几乎都用不到，这个范围已经足够了
        if "\u4e00" <= s <= "\u9fef":
            hans_total += 1
    return hans_total


def count_content(d=-1):
    """每天统计一次昨天的“随手写”字数，并更新进度"""
    group_id = "4e784292-6a65-471e-9f80-e91202e3358c"  # "刘娟娟的朋友圈"
    trxs = client.group.content(group_id)
    rlt = {}
    for trx in trxs:
        ts = client.ts2datetime(trx["TimeStamp"])  # trx日期
        checkts = (datetime.datetime.now() + datetime.timedelta(days=d)).date()  # 统计日期
        if ts.date() == checkts:
            text = client.trx.trx_text(trx)
            if text != "":
                rlt[str(ts)[:19]] = text

    # 今天字数
    n = sum([hans_count(i) for i in rlt.values()])
    note = f"{checkts} 随手写 {len(rlt)} 条，共计 {n} 字。{'' if n >= 1000 else '未能'}完成当天小目标。"
    client.group.send_note(group_id, content=note)


def view_group_info():
    """每天统计一次 seednet 的数据概况并把结果发布到当前 group"""

    groups = {
        "去中心微博": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "刘娟娟的朋友圈": "4e784292-6a65-471e-9f80-e91202e3358c",
        "你好世界": "d87b93a3-a537-473c-8445-609157f8dab0",
        "待办清单": "5d53968c-3b48-44c5-953f-0abe0b7ad73d",
        "Huoju在Rum上说了啥": "f1bcdebd-4f1d-43b9-89d0-88d5fc896660",
        "Ta们在微博上发了啥": "e5f22800-9ab6-4ec7-9795-bc7bd12f800a",
        "种子大全": "89703dbe-93c6-4be0-ba26-dce563181194",
        "去中心推特": "bd119dd3-081b-4db6-9d9b-e19e3d6b387e",
    }

    # 统计指定组的数据，并发到本组
    for gname in groups:
        GroupStatistics(**client_params).view_to_post(groups[gname])


def coin_price():
    """网络可能连不上，需检查"""
    groups = {
        "BTC": "fed57711-8aed-4944-bf9b-d15420d17f4b",
        "ETH": "b280446c-3562-4277-b14e-be7a15bb4718",
    }

    texts = price_texts()
    for symbol in texts:
        if symbol in groups:
            Group(groups[symbol], RUMAPI).post_text(texts[symbol])


def huoju():
    # huoju 在不同 group 的pubkey，人工识别，加入进来。

    names_info = {
        # 去中心微博
        "3bb7a3be-d145-44af-94cf-e64b992ff8f0": [
            "CAISIQODbcx2zjXC6AVGFNk3rzfoydQrIfXUu5FDD092fICQLA=="
        ],
        # 去中心贴吧
        "c15bbb96-5ea0-4160-9d0f-4fbd731df59c": [
            "CAISIQIWBA6Ipmztu5PW0LYfhuRuziqbnKnSI/mrb2kVDQ3v5Q=="
        ],
        # 去中心推特
        "bd119dd3-081b-4db6-9d9b-e19e3d6b387e": [
            "CAISIQN88AYbpppS6WuaYCE0/2OX+QSzq6IYgigwAodETppmGQ=="
        ],
        "18fe26fe-1cd8-415e-9f58-b0fca6b7fcf1": [
            "CAISIQMcWrnqLvk6lkU0zwlD9JSzNYYqaSK+6HTn+uk1LqF/wA==",
            "CAISIQLr1AvvZAwjpHjUSCE9dHC9fLHT8Ybl2FHyHaHg6OlCcA==",
        ],
        "0e4394a5-ba9f-4aeb-ac67-f79623eb05a9": [
            "CAISIQOf5iTCkKHjKWJ9MQPNda/3ABqKuvOZs/95Nj7sAVOKGw=="
        ],
        "b7a0b7a4-ff3f-4789-a088-d53cb2d82275": [
            "CAISIQLu1sz1SvtA+4115PgvnmCWBngBpsAY7fCbytURUm3yyw=="
        ],
    }

    name = "Huoju"
    # 本地数据文件，用来标记哪些动态已转发
    filepath = homedir + r"\examples\whosays\huoju_says.json"

    client = WhoSays(**client_params)

    data = JsonFile(filepath).read()
    data = client.search(names_info, data)
    JsonFile(filepath).write(data)
    # 测试用，如果你也尝试，改为自己创建的组
    group_id = "3c5c16f6-8838-4975-babd-e8c86e0e9ac1"
    # 正式用的，请不要往正式组发测试数据，否则会被加入黑名单
    group_id = "f1bcdebd-4f1d-43b9-89d0-88d5fc896660"

    data = client.send(name, group_id, data)
    JsonFile(filepath).write(data)


def init_task():
    # 待办清单
    group_id = "5d53968c-3b48-44c5-953f-0abe0b7ad73d"
    tasks = [f"TODO:{datetime.date.today()} 平举双臂 1 分钟。"]
    for task in tasks:
        client.group.send_note(group_id, content=task)


def search_seeds():

    # 初始化
    client = SearchSeeds(**client_params)
    # 数据文件
    dirpath = f"{os.path.realpath('.')}\\examples\\search_seeds\\data"
    Dir(dirpath).check_dir()
    filepath = f"{dirpath}\\search_seeds_and_joined_data.json"
    data = JsonFile(filepath).read()

    # 搜寻种子并更新数据文件
    data = client.search_seeds(data)
    JsonFile(filepath).write(data)

    # 离开某些种子网络，比如大量测试用种子
    # is_block 为真，表示离开区块数为 0 的种子网络；为否表示不离开
    # 离开过的种子网络会自动标记不值得加入，避免以后重复加入
    toleave_groupnames = [
        "测试hellorum",
        "测试whosays",
        "测试种子大全",
        "新增测试组",
        "nihao",
        "nihao3",
        "测试一下",
        "测试一下下",
    ]

    data = client.leave_group(data, toleave_groupnames, is_block=True)
    JsonFile(filepath).write(data)

    # 加入未曾加入的种子网络
    data = client.join_group(data)
    JsonFile(filepath).write(data)

    # 分享到种子网络
    group_id = "89703dbe-93c6-4be0-ba26-dce563181194"  # 种子大全
    data = client.share(data, group_id)
    JsonFile(filepath).write(data)

    group_id = "5eae9761-4a2f-4302-8e24-95332a1c299b"  # 种子精选
    data = client.share(data, group_id)
    JsonFile(filepath).write(data)


def mixtask():

    done = JsonFile(logsfile).read()

    while True:
        dd = datetime.datetime.now()
        d = dd.day
        h = dd.hour
        m = dd.minute

        if done["init_task"] != d:
            init_task()
            done["init_task"] = d
            JsonFile(logsfile).write(done, is_print=False)

        if done["count_content"] != d:
            count_content()
            done["count_content"] = d
            JsonFile(logsfile).write(done, is_print=False)

        if done["view_group_info"] != d:
            view_group_info()
            done["view_group_info"] = d
            JsonFile(logsfile).write(done, is_print=False)

        if done["huoju"] != m // 10:
            huoju()
            done["huoju"] = m // 10
            JsonFile(logsfile).write(done, is_print=False)

        if done["search_seeds"] != m // 10:
            # 种子大全
            search_seeds()
            done["search_seeds"] = m // 10
            JsonFile(logsfile).write(done, is_print=False)

        while datetime.datetime.now().minute // 10 == m // 10:
            sleep(300)


if __name__ == "__main__":
    mixtask()
