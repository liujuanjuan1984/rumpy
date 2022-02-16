# -*- coding: utf-8 -*-

import os
import sys
from group_statistics import GroupStatistics
from config import Config
from officepy import JsonFile

client = GroupStatistics(**client_params)

groups = {
    "测试TODO": "abc01f11-6890-4cd3-8234-0b920c6b7085",
    # "刘娟娟的朋友圈": "4e784292-6a65-471e-9f80-e91202e3358c",
}

# 统计指定组的数据，并发到本组
for gname in groups:
    client.view_to_post(groups[gname])


# 统计 A 组数据，结果发送到 B 组
toview = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"  # 待统计的组
toshare = "4e784292-6a65-471e-9f80-e91202e3358c"  # 接收统计结果的组

client.view_to_post(toview, toshare)

# 统计A 组数据，但不想发送，结果可保存到本地 .json 文件
toview = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"  # 待统计的组
client.view_to_save(toview, "temp.json")
