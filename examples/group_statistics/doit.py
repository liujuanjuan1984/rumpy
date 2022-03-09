import os
import datetime
from rumpyconfig import RumpyConfig
from officepy import JsonFile
from group_statistics import GroupStatistics

client = GroupStatistics(**RumpyConfig.GUI)

progressfile = os.path.join(os.path.dirname(__file__), "data", "progress.json")
progress = JsonFile(progressfile).read({})

toshare = "48b74295-a08c-40d4-99eb-5121e810c180"  # client.group.create("mytest_groupview")["group_id"]

for gid in client.node.groups_id:
    if client.group.info(gid).highest_height > 50:
        today = str(datetime.date.today())
        if progress.get(gid) != today:
            progress[gid] = today
            client.view_to_post(gid)
            # client.view_to_post(gid, toshare)

JsonFile(progressfile).write(progress)
