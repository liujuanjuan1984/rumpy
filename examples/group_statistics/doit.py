import os
import datetime
from officy import JsonFile
from group_statistics import GroupStatistics

client = GroupStatistics()

progressfile = os.path.join(os.path.dirname(__file__), "data", "progress.json")
progress = JsonFile(progressfile).read({})

toshare = "938455b8-9683-4d06-abae-b422c89103b6"  # client.group.create("mytest_groupview")["group_id"]

for gid in client.node.groups_id:
    client.group_id = gid
    if client.group.info().highest_height > 50:
        today = str(datetime.date.today())
        if progress.get(gid) != today:
            progress[gid] = today

            # client.view_to_post(gid)
            client.view_to_post(gid, toshare)

JsonFile(progressfile).write(progress)
