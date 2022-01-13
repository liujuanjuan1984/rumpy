# -*- coding: utf-8 -*-

import datetime
import sys

sys.path.append(r"D:\Jupyter\rumpy")  # 修改为你本地的 rumpy 地址
from rumpy import RumClient


def main():

    # 初始化
    kwargs = {
        "appid": "peer",
        "host": "127.0.0.1",
        "port": 55043,  # 需修改为：你的 quorum 的网络端口号
        "cacert": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",  # 需修改为：你的本地 server.crt 文件路径
    }
    client = RumClient(**kwargs)

    # 创建一个新组，用来测试
    seed = client.group.create("测试hellorum")
    group_id = seed["group_id"]

    # 往该组内发布内容、点赞、评论等
    kwargs = {"content": str(datetime.datetime.now()) + " 只有文本"}
    resp1 = client.group.send_note(group_id, **kwargs)

    kwargs = {
        "content": str(datetime.datetime.now()) + " 有文有图",
        "image": [r"D:\Jupyter\rumpy\examples\hellorum\girl.png"],  # 需修改为：你本地的一张图片的路径
    }
    resp2 = client.group.send_note(group_id, **kwargs)

    kwargs = {
        "content": str(datetime.datetime.now()) + " 评论`只有文本`的那条",
        "inreplyto": resp1["trx_id"],
    }
    resp3 = client.group.send_note(group_id, **kwargs)

    kwargs = {
        "content": str(datetime.datetime.now()) + " 评论`有文有图`的那条",
        "inreplyto": resp2["trx_id"],
    }
    resp4 = client.group.send_note(group_id, **kwargs)

    kwargs = {
        "content": str(datetime.datetime.now()) + " 对评论的回复",
        "inreplyto": resp4["trx_id"],
    }
    resp5 = client.group.send_note(group_id, **kwargs)

    # 喜欢
    client.group.like(group_id, resp1["trx_id"])
    client.group.like(group_id, resp2["trx_id"])
    client.group.like(group_id, resp3["trx_id"])
    client.group.like(group_id, resp4["trx_id"])
    client.group.like(group_id, resp5["trx_id"])

    # 取消喜欢
    client.group.dislike(group_id, resp1["trx_id"])

    # 查看该组的信息
    info = client.group.info(group_id)
    print(info)

    # 查看节点的信息
    print(client.node.id)
    print(client.node.status)


if __name__ == "__main__":
    main()
