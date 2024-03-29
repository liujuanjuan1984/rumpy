import datetime

from rumpy import FullNode

TEST_GROUPS_TO_LEAVE = [
    "mytest_group",
]


def main(is_create_new=False):
    """is_create_new: create new group for test"""
    client = FullNode()
    my_test_groups = ["mytest_leave_groups"]

    print(datetime.datetime.now(), "groups num: ", len(client.api.groups_id))
    print(TEST_GROUPS_TO_LEAVE + my_test_groups)

    # create group for test
    if is_create_new:
        for name in my_test_groups:
            group_id = client.api.create_group(name)["group_id"]
            print(datetime.datetime.now(), "leave seednet: ", name, group_id)

    # leave groups
    for group_id in client.api.groups_id:
        client.group_id = group_id
        info = client.api.group_info()
        name = info.get("group_name")

        # name in the list:
        if name in my_test_groups + TEST_GROUPS_TO_LEAVE:
            client.api.leave_group()
            print(
                datetime.datetime.now(),
                "leave seednet: ",
                name,
                group_id,
                "name in TEST_GROUPS_TO_LEAVE.",
            )
        # name include mytest_
        elif name.find("mytest_") >= 0:
            client.api.leave_group()
            print(
                datetime.datetime.now(),
                "leave seednet: ",
                name,
                group_id,
                "name with `mytest_`.",
            )
        # the group with 0 blocks
        elif info.get("highest_height") == 0:
            client.api.leave_group()
            print(
                datetime.datetime.now(),
                "leave seednet: ",
                name,
                group_id,
                "highest_height is 0.",
            )

    print(datetime.datetime.now(), "groups num: ", len(client.api.groups_id))
    print(datetime.datetime.now(), "TIPS: IF YOU'RE USING THE GUI APP,RELOAD IT.")


if __name__ == "__main__":
    main(is_create_new=False)
