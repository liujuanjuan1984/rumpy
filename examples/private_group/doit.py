from rumpyconfig import RumpyConfig
from private_group import PrivateGroup

"""
owner: 先create后，announce自己，等待trx上链后，再approve自己，上链后，自己就成功了。
user: 先announce自己，等待owner查询到该申请后approve后，就可以了。
"""

bot = PrivateGroup(**RumpyConfig.GUI)

bot.group_id = "e1c80c48-df26-44e9-9db3-b305d99fcd07"
pubkey = None


text = """
0 byebye
1 create private group
2 annouce self
3 approve (only owner can)
4 users
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
