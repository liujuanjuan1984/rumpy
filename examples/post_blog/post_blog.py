import time
import datetime
import pytest
import os
import sys
from officepy import JsonFile, Dir
from rumpy import RumClient
from config import Config


client = RumClient(**Config.CLIENT_PARAMS["gui"])

# create a group
group_id = client.group.create("mytest_postblog", app_key="group_post")["group_id"]

# get the articles file for test
test_data_dir = os.path.join(os.path.dirname(__file__),"test_data")
article_files = Dir(test_data_dir).search_files_by_types((".md".".txt"))

# post to rum
failed = []
for ifile in article_files:
    with open(ifile, "r", encoding="utf-8") as f:
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
        failed.append(ifile)
    time.sleep(1)

print(failed)
