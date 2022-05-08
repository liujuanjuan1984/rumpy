import os
from officy import JsonFile
from whosays import WhoSays


seedsfile = r"D:\Jupyter\seeds\data\seeds.json"


def trans():
    bot = WhoSays()
    bot.init("huoju", seedsfile)

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

    bot = WhoSays(port=58356)
    bot.init("huoju", seedsfile)
    bot.search()
    bot.check_data()
    group_id = bot.group.create("mytest_whosays")["group_id"]
    bot.send("HuoJu", group_id)


if __name__ == "__main__":
    main()
