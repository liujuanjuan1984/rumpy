import os

from officy import JsonFile
from whosays import WhoSays


def trans():
    bot = WhoSays()
    bot.init("huoju")

    oldfile = os.path.join(os.path.dirname(__file__), "data", "huoju", "huoju_says.json")
    olddata = JsonFile(oldfile).read()
    newdata = JsonFile(bot.datafile).read()

    toshare_group_id = "f1bcdebd-4f1d-43b9-89d0-88d5fc896660"
    for group_id in olddata:
        trxs = olddata[group_id]["trxs"]
        for trx_id in trxs:
            if (
                toshare_group_id in (trxs[trx_id].get("shared") or [])
                and toshare_group_id not in newdata[group_id][trx_id]["shared"]
            ):
                newdata[group_id][trx_id]["shared"].append(toshare_group_id)
    JsonFile(bot.datafile).write(newdata)


def main():

    bot = WhoSays()
    bot.init("huoju")
    bot.search()
    group_id = bot.api.create_group("mytest_whosays")["group_id"]
    bot.send("HuoJu", group_id)


if __name__ == "__main__":
    main()
