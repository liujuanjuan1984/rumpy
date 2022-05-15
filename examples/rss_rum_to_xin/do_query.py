from bot import bot
from modules import *


def count_users():

    print("🤖 Rss Rum to Xin bot 7000104017 🤖")
    print("=== 每个种子网络的订阅数 ===")
    counts = {}
    for g in bot.groups:
        _c = bot.db.session.query(BotRss).filter(BotRss.group_id == g.group_id).all()
        counts[g.group_name] = len(_c)
    countsit = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for name, n in countsit:
        print(n, name)

    _c = bot.db.session.query(BotRss).filter(BotRss.user_id).all()
    print("🥂 共计", len(_c), "个用户使用 bot🥂")


all = bot.db.session.query(BotRss).all()
for i in all:
    print(i)
