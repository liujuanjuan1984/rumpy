from bot import bot
from modules import BotAirDrops
from config_rss import my_rum_group

bot.airdrop_to_group(my_rum_group)
bot.airdrop_to_node()
bot.airdrop_to_bot()

rlts = bot.db.session.query(BotAirDrops).all()
for r in rlts:
    print(r.num, r.memo, r.mixin_id)
