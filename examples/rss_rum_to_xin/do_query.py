from bot import bot
from modules import *


all = bot.db.session.query(BotRss).all()
for i in all:
    print(i)
