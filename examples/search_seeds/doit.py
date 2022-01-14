# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.realpath("."))
from search_seeds import SearchSeeds
from rumpy import JsonFile, Dir
from examples.config import client_params


def main():
    # 初始化
    client = SearchSeeds(**client_params)
    # 数据文件
    dirpath = os.path.realpath(".") + "\\examples\\search_seeds\\data"
    Dir(dirpath).check_dir()
    filepath = dirpath + "\\search_seeds_and_joined_data.json"
    # 搜寻种子
    client.search_seeds(filepath)
    # 离开指定的种子网络，比如测试用的
    toleave_groupnames = [
        "测试hellorum",
        "测试whosays",
        "新增测试组",
        "nihao",
        "nihao3",
        "测试一下",
        "测试一下下",
    ]
    # is_block 为真，表示离开区块数为 0 的种子网络；为否则不离开
    # 离开过的种子网络会自动标记不值得加入，避免以后重复加入
    client.leave_group(filepath, toleave_groupnames, is_block=True)
    # 加入未曾加入的种子网络
    client.join_group(filepath)


if __name__ == "__main__":
    main()
