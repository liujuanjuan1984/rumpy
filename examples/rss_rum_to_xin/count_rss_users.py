import os
from officy import JsonFile
from config_rss import *


# read data
rum_groups_to_view = JsonFile(rum_groups_to_view_file).read({})
rss = JsonFile(rss_file).read({})

print("🤖 Rss Rum to Xin bot 7000104017 🤖")
print("=== 每个种子网络的订阅数 ===")

counts = {}
for gid in rss:
    counts[rum_groups_to_view[gid]["group_name"]] = len(rss[gid])
countsit = sorted(counts.items(), key=lambda x: x[1], reverse=True)
for name, n in countsit:
    print(n, name)


cids = []
for gid in rss:
    for cid in rss[gid]:
        if cid not in cids:
            cids.append(cid)

print("🥂 共计", len(cids), "个用户使用 bot🥂")
