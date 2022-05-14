import datetime, time
from bot import bot

while True:
    print(datetime.datetime.now(), "new round", "+" * 40)
    bot.do_rss()
    time.sleep(10)
