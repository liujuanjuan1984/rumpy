from rumpy import FullNode, LightNode
from rumpy.bots.group_statistics import GroupStatistics
from rumpy.exceptions import ParamValueError

client = FullNode()  # LightNode()
bot = GroupStatistics(client)


def do_group(group_id):
    bot.view_to_post(group_id)


def do_node(toshare):
    for gid in client.api.groups_id:
        try:
            bot.view_to_post(gid, toshare)
        except ParamValueError as e:
            print(e)


if __name__ == "__main__":
    text = "0 byebye\n1 刘娟娟的朋友圈\n2 去中心微博\n3 当前节点所有（发送到自定义测试组)\n>>>"
    asku = input(text)
    if asku == "1":
        group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
        do_group(group_id)
    elif asku == "2":
        group_id = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"
        do_group(group_id)
    elif asku == "3":
        toshare = client.api.create_group("mytest_groupview")["group_id"]
        do_node(toshare)
    else:
        print("byebye.")
