# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.realpath("."))
from rumpy import RumClient
from examples.config import client_params


def main(is_create_new=False):
    # 初始化
    client = RumClient(**client_params)

    my_test_groups = [
        "测试hellorum",
        "测试whosays",
        "新增测试组",
        "nihao",
        "nihao3",
        "测试一下",
        "测试一下下",
    ]

    # 创建一些组用来测试
    if is_create_new:
        for i in my_test_groups:
            group_id = client.group.create(i)["group_id"]
            print("已创建种子网络", i, group_id)

    # 离开满足某些条件的组
    for group_id in client.node.groups_id:
        info = client.group.info(group_id)
        name = info.group_name

        # 退出本人创建的测试组
        if client.group.is_mygroup(group_id):  # 是本人创建的
            if name in my_test_groups:  # 名字在上述列表中
                client.group.leave(group_id)
                print("已离开种子网络", name, group_id)

        # 退出区块数为 0 的 group
        if info.highest_height == 0:
            client.group.leave(group_id)
            print("已离开种子网络", name, group_id)

    print("TIPS: 如果你正开着桌面应用观察效果，可以点击左上角的“重新加载”刷新页面。")


if __name__ == "__main__":
    main(is_create_new=False)
