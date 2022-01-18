# -*- coding: utf-8 -*-

import time
import datetime
import pytest
import os
import sys

sys.path.append(os.path.realpath("."))
from rumpy import JsonFile, RumClient, Dir
from examples.config import client_params


client = RumClient(**client_params)

# 创建测试组
group_id = client.group.create("测试一下", app_key="group_post")["group_id"]

# 用来存放需要自动发布文章的本地文件夹
mds = Dir(r"D:\MY-OBSIDIAN-DATA\my_Writing\完整文章").search_files_by_types(".md")

# 自动读取并一次性发布
failed = []
for imd in mds:
    with open(imd, "r", encoding="utf-8") as f:
        ilines = f.readlines()
        for line in ilines:
            if line.startswith("# "):
                title = line.replace("# ", "").replace("\n", "")
                n = ilines.index(line)
                break
        content = "".join(ilines[n + 1 :])

    objs = {"content": content, "name": title}
    resp = client.group.send_note(group_id, **objs)
    if "trx_id" not in resp:
        failed.append(imd)
    time.sleep(1)

print(failed)
