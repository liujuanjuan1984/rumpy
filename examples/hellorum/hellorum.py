import datetime
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

    # 创建一个新组，用来测试
    seed = bot.group.create("测试hellorum")
    group_id = seed["group_id"]

    # 往组内发布内容、点赞、评论等
    kwargs = {"text": str(datetime.datetime.now()) + " 只有文本"}
    resp1 = bot.group.send_note(group_id, **kwargs)

    kwargs = {
        "text": str(datetime.datetime.now()) + " 有文有图",
        "imgs": [r"D:\Jupyter\rumpy\examples\hellorum\girl.png"],
    }
    resp2 = bot.group.send_note(group_id, **kwargs)

    kwargs = {
        "text": str(datetime.datetime.now()) + " 评论`只有文本`的那条",
        "trx_id": resp1["trx_id"],
    }
    resp3 = bot.group.send_note(group_id, **kwargs)

    kwargs = {
        "text": str(datetime.datetime.now()) + " 评论`有文有图`的那条",
        "trx_id": resp2["trx_id"],
    }
    resp4 = bot.group.send_note(group_id, **kwargs)

    kwargs = {
        "text": str(datetime.datetime.now()) + " 对评论的回复",
        "trx_id": resp4["trx_id"],
    }
    resp5 = bot.group.send_note(group_id, **kwargs)

    # 喜欢
    bot.group.like(group_id, resp1["trx_id"])
    bot.group.like(group_id, resp2["trx_id"])
    bot.group.like(group_id, resp3["trx_id"])
    bot.group.like(group_id, resp4["trx_id"])
    bot.group.like(group_id, resp5["trx_id"])
    # 取消喜欢
    bot.group.dislike(group_id, resp1["trx_id"])


if __name__ == "__main__":
    main()
