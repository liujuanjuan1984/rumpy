from rumpyconfig import RumpyConfig
from private_group import PrivateGroup

"""
owner: 先create后，announce自己，等待trx上链后，再approve自己，上链后，自己就成功了。
user: 先announce自己，等待owner查询到该申请后approve后，就可以了。
"""

bot = PrivateGroup(**RumpyConfig.GUI)

bot.group_id = "b0ab786f-4deb-41e4-b4f0-509da71d4ef2"
pubkey = None


text = """
0 byebye
1 create private group
2 annouce self
3 approve (only owner can)
4 view users
5 view trxs
6 post sth.
>>>"""

asku = input(text)
if asku == "1":
    r = bot.create("mytest_private")
    print(r)
elif asku == "2":
    r = bot.announce("test private group to join.")
    print(r)
elif asku == "3":
    pubkey = pubkey or bot.group.pubkey
    r = bot.approve(pubkey)
    print(r)
elif asku == "4":
    r = bot.users()
    print(r)
elif asku == "5":
    r = bot.group.content_trxs()
    for trx in r:
        print(
            trx["TrxId"],
            "SEE:",
            trx.get("Content") != {},
            "ME:",
            trx["Publisher"] == bot.group.pubkey,
        )
    print(len(r), "条trxs")
elif asku == "6":
    r = bot.group.send_note(content=input("say something>>>"))
    print(r)
