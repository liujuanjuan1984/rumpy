# -*- coding: utf-8 -*-

import sys

sys.path.append(r"D:\Jupyter\rumpy")  # 修改为你本地的 rumpy 地址
from rumpy import RumClient


def main():

    # 初始化
    kwargs = {
        "appid": "peer",
        "host": "127.0.0.1",
        "port": 55043,  # 修改为你的 quorum 的网络端口号
        "cacert": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",  # 修改为你的本地 server.crt 文件路径
    }
    bot = RumClient(**kwargs)

    # 获取已经加入的所有组
    for gdata in bot.node.groups():
        # 只离开自己自己创建的组
        if gdata["owner_pubkey"] != bot.node.pubkey:
            continue
        # 这些是之前测试时大量创建的组，可离开
        if gdata["group_name"] in ["测试hellorum", "测试whosays", "新增测试组", "nihao"]:
            bot.group.leave(gdata["group_id"])

    print("如果开着桌面应用GUI，可以点击左上角的“重新加载”刷新页面。")


if __name__ == "__main__":
    main()
