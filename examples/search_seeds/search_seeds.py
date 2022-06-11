import datetime
import json
import re
from typing import Dict, List

from officy import JsonFile

import rumpy.utils as utils
from rumpy import FullNode

DONT_JOIN = ["测试一下", "测试一下下", "nihao3", "nihao"]
DONT_JOIN_PIECES = ["mytest_", "测试", "test"]


class SearchSeeds(FullNode):
    def init_app(self, seedsfile, progressfile, infofile):
        self.seedsfile = seedsfile
        self.progressfile = progressfile
        self.infofile = infofile

    def intext(self, text: str) -> List:
        """
        Search seeds in text, return list of seeds.
        Only one seed in text can be found.
        """
        seeds = []
        pt = r"""({['"].*genesis_block.*['"]})"""
        for i in re.findall(pt, text or "", re.S):
            try:
                iseed = json.loads(i)
                if utils.is_seed(iseed):
                    seeds.append(iseed)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(e)
                continue
        return seeds

    def intrx(self, trx: Dict) -> List:
        """Search seeds in trx, return list of seeds."""
        return self.intext(trx["Content"].get("content") or "")

    def ingroup(self, trx_id=None, flag=True) -> Dict:
        """Search seeds in group, and write result to datafile."""

        logs = JsonFile(self.progressfile).read({})
        seeds = JsonFile(self.seedsfile).read({})

        if self.group_id not in logs:
            logs[self.group_id] = None

        trx_id = logs[self.group_id]

        if self.group_id not in seeds:
            seed = self.api.seed()
            if seed:
                seeds[self.group_id] = seed

        trxs = self.api.get_group_all_contents(trx_id=trx_id)

        for trx, tid in trxs:
            for seed in self.intrx(trx):
                if seed["group_id"] not in seeds:
                    seeds[seed["group_id"]] = seed

        logs[self.group_id] = utils.get_last_trxid_by_ts(trxs)
        JsonFile(self.seedsfile).write(seeds)
        JsonFile(self.progressfile).write(logs)

    def innode(self) -> Dict:
        """Search seeds in node."""
        for group_id in self.api.groups_id:
            self.group_id = group_id
            self.ingroup()

    def update_status(self):
        """从已加入的种子网络中搜索新的种子，并更新数据文件"""

        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data
        joined = self.api.groups_id

        for group_id in seeds:
            if group_id not in info:
                info[group_id] = {
                    "highest_height": -1,
                    "last_update": "init",
                    "nodes": {},
                    "scores": 0,
                }
            if "abandoned" not in info[group_id]:
                info[group_id]["abandoned"] = False

        for group_id in joined:
            self.group_id = group_id
            ginfo = self.api.group_info()
            gts = self.api.block(ginfo.highest_block_id).get("TimeStamp")
            if ginfo.highest_height > info[group_id]["highest_height"]:
                info[group_id]["highest_height"] = ginfo.highest_height
                info[group_id]["last_update"] = f"{utils.utils.timestamp_to_datetime(gts)}"
                info[group_id]["scores"] += int(ginfo.highest_height / 100)
                info[group_id]["nodes"][ginfo.user_pubkey] = f"{datetime.datetime.now()}"

        JsonFile(self.infofile).write(info)
        return info

    def join_groups(self):
        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data

        for group_id in seeds:
            if group_id in self.api.groups_id:
                continue
            if (info[group_id].get("scores") or 0) < 0:
                continue
            gname = seeds[group_id]["group_name"]
            if gname in DONT_JOIN:
                continue

            is_join = True
            for piece in DONT_JOIN_PIECES:
                if gname.find(piece) >= 0:
                    is_join = False
                    break
            if not is_join:
                continue
            resp = self.api.join_group(seeds[group_id])

        self.update_status()

    def leave_groups(self):
        info = self.update_status()
        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        joined = self.api.groups_id

        for group_id in joined:
            self.group_id = group_id
            if info[group_id].get("scores") or 0 >= 0:
                continue

            gname = seeds[group_id]["group_name"]
            if gname not in DONT_JOIN:
                continue
            ginfo = self.api.group_info()
            if info[group_id][ginfo.user_pubkey] <= "2022-01-01" and (
                info[group_id]["last_update"] <= "2022-01-01" or info[group_id]["highest_height"] == 0
            ):

                self.api.leave_group()
                continue

            for piece in DONT_JOIN_PIECES:
                if gname.find(piece) >= 0:
                    is_leave = True
                    break

            if is_leave:
                print(self.group_id, "leave the group.")
                self.api.leave_group()
        self.update_status()

    def worth_toshare(self, group_id):
        self.group_id = group_id
        info = self.api.group_info()

        # 区块高度 小于等于 3
        if info.highest_height <= 3:
            return False

        # 最后更新时间在 7 天前
        sometime = datetime.datetime.now() + datetime.timedelta(days=-7)
        lasttime_upd = utils.utils.timestamp_to_datetime(info.last_updated)
        if lasttime_upd < sometime:
            return False

        return f"""\n区块高度:{info.highest_height}\n最后更新: {lasttime_upd}\n"""

    def share(self, data, group_id=None):
        """检查种子是否在该group被分享过"""

        self.group_id = group_id

        # 如果没有指定 group_id 或未加入，就新建种子网络
        if self.group_id == None or not self.api.is_joined():
            self.group_id = group_id = self.api.create_group("mytest_share_seeds")["group_id"]

        shared = self.ingroup(group_id)

        for gid in data:
            # 跳过已经分享过的
            if gid in shared:
                continue
            # 跳过不值得分享或加入的
            if not data[gid]["is_worth"]:
                continue
            # 跳过没有加入的
            if not data[gid]["is_joined"]:
                continue

            text = self.worth_toshare(gid)
            # 跳过其它条件不值得分享的
            if not text:
                continue
            # 分享到指定组
            text = f'{json.dumps(data[gid]["seed"])}{text}'
            resp = self.api.send_note(content=text)

            # 跳过没有推送成功的
            if "trx_id" not in resp:
                continue
            # 推送成功，更新数据
            if "share_at" not in data[gid]:
                data[gid]["share_at"] = [group_id]
            else:
                data[gid]["share_at"].append(group_id)

            data[gid]["update_at"] = str(datetime.datetime.now())
        return data
