import datetime
import json
import re
from typing import Dict, List
from rumpy import RumClient
from officepy import Stime, JsonFile

DONT_JOIN = ["测试一下", "测试一下下", "nihao3", "nihao"]
DONT_JOIN_PIECES = ["mytest_"]


class SearchSeeds(RumClient):
    def init_app(self, datafile, logfile, trxfile, infofile):
        self.datafile = datafile
        self.logfile = logfile
        self.trxfile = trxfile
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
                if self.node.is_seed(iseed):
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

    def __ingroup(self, group_id: str, trx_id: str, seedsdata: Dict) -> Dict:
        """Search seeds in group, return list of seeds."""

        checked = JsonFile(self.trxfile).read({})
        trxs = self.group.content_trxs(group_id, trx_id, num=50)
        print(datetime.datetime.now(), trx_id, len(trxs), end=" ")
        if len(trxs) == 0:
            # False means no need to continue
            return False, trx_id, seedsdata

        for trx in trxs:
            tid = trx["TrxId"]
            if not checked.get(tid):
                trx_id = tid
                for seed in self.intrx(trx):
                    gid = seed["group_id"]
                    if gid not in seedsdata:
                        seedsdata[gid] = seed
            checked[tid] = f"{datetime.datetime.now()}"
        print(trx_id)
        JsonFile(self.trxfile).write(checked)
        return True, trx_id, seedsdata  # True means need to continue

    def ingroup(self, group_id: str, trx_id=None, seedsdata={}, flag=True) -> Dict:
        """Search seeds in group, and write result to datafile."""

        logs = JsonFile(self.logfile).read({})
        seedsdata = seedsdata or JsonFile(self.datafile).read({})
        if group_id not in logs:
            logs[group_id] = []

        if len(logs[group_id]) > 0:
            trx_id = logs[group_id][-1]["trx_id"] or trx_id
        if group_id not in seedsdata:
            seedsdata[group_id] = self.group.seed(group_id)

        while flag:
            logs[group_id].append(
                {
                    "trx_id": trx_id,
                    "status": "begin",
                    "time": f"{datetime.datetime.now()}",
                }
            )
            flag, xtrx_id, seedsdata = self.__ingroup(group_id, trx_id, seedsdata)
            logs[group_id].append(
                {
                    "trx_id": trx_id,
                    "status": "done",
                    "time": f"{datetime.datetime.now()}",
                }
            )
            JsonFile(self.datafile).write(seedsdata)
            JsonFile(self.logfile).write(logs)
            if xtrx_id == trx_id:
                break
            else:
                trx_id = xtrx_id

    def innode(self) -> Dict:
        """Search seeds in node."""
        for group_id in self.node.groups_id:
            self.ingroup(group_id)

    def update_status(self):
        """从已加入的种子网络中搜索新的种子，并更新数据文件"""

        seeds = JsonFile(self.datafile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data
        joined = self.node.groups_id

        for group_id in seeds:
            if group_id not in info:
                info[group_id] = {"scores": 0}

        for group_id in joined:
            ginfo = self.group.info(group_id)
            gts = self.group.block(group_id, ginfo.highest_block_id).get("TimeStamp")
            info[group_id].update(
                {
                    self.node.id: f"{datetime.datetime.now()}",
                    "highest_height": ginfo.highest_height,
                    "last_update": f"{Stime().ts2datetime(gts)}",
                }
            )
            info[group_id]["scores"] += 1

        for group_id in info:
            if self.node.id in info[group_id] and group_id not in joined:
                info[group_id].remove(self.node.id)
                info[group_id]["scores"] -= 1

        JsonFile(self.infofile).write(info)
        return info

    def join_groups(self):
        seeds = JsonFile(self.datafile).read({})  # all the seeds
        info = JsonFile(self.infofile).read({})  # status data

        for group_id in seeds:

            if group_id in self.node.groups_id:
                continue
            if info[group_id].get("scores") or 0 < 0:
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
            resp = self.node.join_group(seeds[group_id])

        self.update_status()

    def leave_groups(self):
        info = self.update_status()
        seeds = JsonFile(self.datafile).read({})  # all the seeds
        joined = self.node.groups_id

        for group_id in joined:
            if info[group_id].get("scores") or 0 >= 0:
                continue

            gname = seeds[group_id]["group_name"]
            if gname not in DONT_JOIN:
                continue

            if info[group_id][self.node.id] <= "2022-01-01" and (
                info[group_id]["last_update"] <= "2022-01-01"
                or info[group_id]["highest_height"] == 0
            ):
                self.group.leave(group_id)
                continue

            for piece in DONT_JOIN_PIECES:
                if gname.find(piece) >= 0:
                    is_leave = True
                    break

            if is_leave:
                self.group.leave(group_id)

        self.update_status()

    def worth_toshare(self, group_id):
        info = self.group.info(group_id)

        # 区块高度 小于等于 3
        if info.highest_height <= 3:
            return False
        # 最后更新时间在 7 天前
        sometime = datetime.datetime.now() + datetime.timedelta(days=-7)
        lu = Stime().ts2datetime(info.last_updated)
        if lu < sometime:
            return False

        return f"""\n区块高度:{info.highest_height}\n最后更新: {str(lu)[:19]}\n"""

    def share(self, data, group_id=None):
        """检查种子是否在该group被分享过"""

        # 如果没有指定 group_id 或未加入，就新建种子网络
        if group_id == None or not self.node.is_joined(group_id):
            group_id = self.group.create("测试种子大全")["group_id"]

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
            resp = self.group.send_text(group_id, text)

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
