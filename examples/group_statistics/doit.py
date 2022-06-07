import datetime
import os

from group_statistics import GroupStatistics
from officy import JsonFile

client = GroupStatistics()

progressfile = os.path.join(os.path.dirname(__file__), "data", "progress.json")
progress = JsonFile(progressfile).read({})

toshare = client.api.create_group("mytest_groupview")["group_id"]

for gid in client.api.groups_id:
    client.group_id = gid
    if client.api.group_info().highest_height > 50:
        today = str(datetime.date.today())
        if progress.get(gid) != today:
            progress[gid] = today

            # client.view_to_post(gid)
            client.view_to_post(gid, toshare)

JsonFile(progressfile).write(progress)
