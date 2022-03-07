import os
from officepy import JsonFile
from whosays import WhoSays
from rumpyconfig import RumpyConfig


def main():

    bot = WhoSays(**RumpyConfig.GUI)
    bot.init("huoju")
    bot.search()
    # group_id = bot.group.create("mytest_whosays")["group_id"]
    # bot.send("HuoJu", group_id)


if __name__ == "__main__":
    main()
