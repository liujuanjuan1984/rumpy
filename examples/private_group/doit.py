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
    resp = bot.create("mytest_private")
    print(resp)
elif asku == "2":
    resp = bot.announce("test private group to join.")
    print(resp)
elif asku == "3":
    pubkey = pubkey or bot.group.pubkey
    resp = bot.approve(pubkey)
    print(resp)
elif asku == "4":
    resp = bot.users()
    for user in resp:
        print(user)
elif asku == "5":
    resp = bot.group.content_trxs()
    for trx in resp:
        print(
            trx["TrxId"],
            "SEE:",
            trx.get("Content") != {},
            "ME:",
            trx["Publisher"] == bot.group.pubkey,
        )
        # print(bot.group.trx(trx["TrxId"]))
    print(len(resp), "条trxs")
elif asku == "6":
    resp = bot.group.send_note(content=input("say something>>>"))
    print(resp)
