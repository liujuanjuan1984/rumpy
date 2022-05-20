from bot import RssBot
from modules import *
from sqlalchemy import and_, distinct


def count_users():
    bot = RssBot()
    print("🤖 Rss Rum to Xin bot 7000104017 🤖")
    print("=== 每个种子网络的订阅数 ===")
    counts = {}
    for group_id in bot.groups:
        _c = (
            bot.db.session.query(distinct(BotRss.user_id))
            .filter(and_(BotRss.group_id == group_id, BotRss.is_rss == True))
            .all()
        )
        counts[bot.groups[group_id]["group_name"]] = len(_c)
    countsit = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for name, n in countsit:
        print(n, name)

    _c = bot.db.session.query(distinct(BotRss.user_id)).all()
    print("🥂 共计", len(_c), "个用户使用 bot🥂")


count_users()
