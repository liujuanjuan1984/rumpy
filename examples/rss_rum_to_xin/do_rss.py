import datetime, time
from bot import bot

while True:
    print(datetime.datetime.now(), "new round", "+" * 40)
    try:
        bot.do_rss()
    except Exception as e:
        print(e)
    time.sleep(10)
