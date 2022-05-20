import datetime
import logging
from bot import RssBot

today = datetime.datetime.now().date()
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    filename=f"airdrop_{today}.log",
    level=logging.DEBUG,
)


bot = RssBot()
bot.airdrop_to_node(memo=f"{today} Rum 种子网络空投")
bot.airdrop_to_bot(memo=f"{today} Rum 订阅器空投")
