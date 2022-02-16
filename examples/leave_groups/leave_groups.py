# -*- coding: utf-8 -*-
import datetime
from rumpy import RumClient
from config import Config


def main(is_create_new=False):
    """is_create_new: create new group for test"""

    client = RumClient(**Config.CLIENT_PARAMS["gui"])

    print(datetime.datetime.now(), "groups num: ", len(client.node.groups_id))

    my_test_groups = ["mytest_leave_groups"]

    # create group for test
    if is_create_new:
        for name in my_test_groups:
            group_id = client.group.create(name)["group_id"]
            print(datetime.datetime.now(), "leave seednet: ", name, group_id)

    # leave groups
    for group_id in client.node.groups_id:
        info = client.group.info(group_id)
        name = info.group_name

        # name in the list:
        if name in my_test_groups + Config.TEST_GROUPS_TO_LEAVE:
            client.group.leave(group_id)
            print(datetime.datetime.now(), "leave seednet: ", name, group_id)
        # name include mytest_
        elif name.find("mytest_") >= 0:
            client.group.leave(group_id)
            print(datetime.datetime.now(), "leave seednet: ", name, group_id)
        # the group with 0 blocks
        elif info.highest_height == 0:
            client.group.leave(group_id)
            print(datetime.datetime.now(), "leave seednet: ", name, group_id)

    print(datetime.datetime.now(), "groups num: ", len(client.node.groups_id))
    print(datetime.datetime.now(), "TIPS: IF YOU'RE USING THE GUI APP,RELOAD IT.")


if __name__ == "__main__":
    main(is_create_new=False)
