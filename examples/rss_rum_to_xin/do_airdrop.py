from bot import bot
from modules import BotAirDrops
from config_rss import *
from officy import JsonFile
import random
import datetime

# bot.airdrop_to_group(my_rum_group)
bot.airdrop_to_node()
# bot.airdrop_to_bot()

_today = datetime.datetime.now().date()


def do_rss():
    done = """"""
    rss = JsonFile(rss_file).read()
    memo = f"{_today} Rum 订阅器空投"
    for group_id in rss:
        for cid in rss[group_id]:
            wallet = rss[group_id][cid].get("user_id")
            if wallet is None:
                continue
            print(wallet)
            if wallet in done:
                continue
            _num = str(round(0.001 + random.randint(1, 100) / 1000000, 6))
            _a = {
                "mixin_id": wallet,
                "group_id": group_id,
                "num": str(_num),
                "token": "RUM",
                "memo": memo,
                "is_sent": False,
            }
            r = bot.xin.api.transfer.send_to_user(wallet, rum_asset_id, _num, memo)

            if "data" in r:
                print(wallet, str(_num), "账户余额：", r.get("data").get("closing_balance"))
                _a["is_sent"] = True

            bot.db.add(BotAirDrops(_a))


rlts = bot.db.session.query(BotAirDrops).all()
for r in rlts:
    print(r.num, r.memo, r.mixin_id)
