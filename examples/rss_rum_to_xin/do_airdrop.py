from bot import bot
from modules import BotAirDrops
from config_rss import *
from officy import JsonFile
import random
import datetime

_today = datetime.datetime.now().date()


bot.airdrop_to_group(group_id=my_rum_group, memo=f"{_today} 刘娟娟的朋友圈空投")
bot.airdrop_to_node(memo=f"{_today} Rum 种子网络空投")
bot.airdrop_to_bot(memo=f"{_today} Rum 订阅器空投")


rlts = bot.db.session.query(BotAirDrops).all()
for r in rlts:
    print(r.num, r.memo, r.mixin_id)
