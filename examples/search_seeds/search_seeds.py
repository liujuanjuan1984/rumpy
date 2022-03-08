import datetime
import json
import re
from typing import Dict, List
from rumpy import RumClient
from officepy import Stime, JsonFile

DONT_JOIN = ["测试一下", "测试一下下", "nihao3", "nihao"]
DONT_JOIN_PIECES = ["mytest_"]


class SearchSeeds(RumClient):
    def init_app(self, seedsfile, logfile, infofile):
        self.seedsfile = seedsfile
        self.logfile = logfile
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
                if self.group.is_seed(iseed):
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

        logs = JsonFile(self.logfile).read({})
        seeds = JsonFile(self.seedsfile).read({})

        if self.group_id not in logs:
            logs[self.group_id] = None

        trx_id = logs[self.group_id]
        checked_tids = []

        if self.group_id not in seeds:
            seed = self.group.seed()
            if seed:
                seeds[self.group_id] = seed

        while flag:
            if trx_id in checked_tids:
                break
            else:
                checked_tids.append(trx_id)

            logs[self.group_id] = trx_id
            trxs = self.group.content_trxs(trx_id=trx_id, num=50)
            print(datetime.datetime.now(), trx_id, len(trxs))

            if len(trxs) == 0:
                break
            for trx in trxs:
                for seed in self.intrx(trx):
                    if seed["group_id"] not in seeds:
                        seeds[seed["group_id"]] = seed

            trx_id = trxs[-1]["TrxId"]
            JsonFile(self.seedsfile).write(seeds)
            JsonFile(self.logfile).write(logs)

    def innode(self) -> Dict:
        """Search seeds in node."""
        for group_id in self.node.groups_id:
            self.group_id = group_id
            self.ingroup()

    def update_status(self):
        """从已加入的种子网络中搜索新的种子，并更新数据文件"""

        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data
        joined = self.node.groups_id

        for group_id in seeds:
            if group_id not in info:
                info[group_id] = {
                    "highest_height": -1,
                    "last_update": "init",
                    "nodes": {},
                    "scores": 0,
                }

        for group_id in joined:
            self.group_id = group_id
            ginfo = self.group.info()
            gts = self.group.block(ginfo.highest_block_id).get("TimeStamp")
            if ginfo.highest_height > info[group_id]["highest_height"]:
                info[group_id]["highest_height"] = ginfo.highest_height
                info[group_id]["last_update"] = f"{Stime.ts2datetime(gts)}"
                info[group_id]["scores"] += int(ginfo.highest_height / 100)
                info[group_id]["nodes"][
                    ginfo.user_pubkey
                ] = f"{datetime.datetime.now()}"

        JsonFile(self.infofile).write(info)
        return info

    def join_groups(self):
        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data

        for group_id in seeds:
            if group_id in self.node.groups_id:
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
            resp = self.group.join(seeds[group_id])

        self.update_status()

    def leave_groups(self):
        info = self.update_status()
        seeds = JsonFile(self.seedsfile).read({})  # all the seeds
        joined = self.node.groups_id

        for group_id in joined:
            self.group_id = group_id
            if info[group_id].get("scores") or 0 >= 0:
                continue

            gname = seeds[group_id]["group_name"]
            if gname not in DONT_JOIN:
                continue
            ginfo = self.group.info(group_id)
            if info[group_id][ginfo.user_pubkey] <= "2022-01-01" and (
                info[group_id]["last_update"] <= "2022-01-01"
                or info[group_id]["highest_height"] == 0
            ):

                self.group.leave()
                continue

            for piece in DONT_JOIN_PIECES:
                if gname.find(piece) >= 0:
                    is_leave = True
                    break

            if is_leave:
                print(self.group_id, "leave the group.")
                self.group.leave()
        self.update_status()

    def worth_toshare(self, group_id):
        self.group_id = group_id
        info = self.group.info()

        # 区块高度 小于等于 3
        if info.highest_height <= 3:
            return False

        # 最后更新时间在 7 天前
        sometime = datetime.datetime.now() + datetime.timedelta(days=-7)
        lasttime_upd = Stime.ts2datetime(info.last_updated)
        if lasttime_upd < sometime:
            return False

        return f"""\n区块高度:{info.highest_height}\n最后更新: {lasttime_upd}\n"""

    def share(self, data, group_id=None):
        """检查种子是否在该group被分享过"""

        # 如果没有指定 group_id 或未加入，就新建种子网络
        if group_id == None or not self.node.is_joined(group_id):
            group_id = self.group.create("mytest_share_seeds")["group_id"]

        shared = self.ingroup(group_id)
        self.group_id = group_id
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
            resp = self.group.send_note(content=text)

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
