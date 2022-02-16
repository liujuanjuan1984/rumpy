import datetime
from typing import Dict, List
import json
import os
from rumpy import RumClient
from officepy import Stime


class SearchSeeds(RumClient):
    def intrx(self, trxdata: Dict) -> List:
        """search seeds from trx data"""
        text = self.trx.trx_text(trxdata).replace("\n", " ")

        if text == "":
            return []

        # 只能识别单个种子，但依然采用列表来处理结果
        seeds = []
        pt = r"^[^\{]*?(\{[\s\S]*?\})[^\}]*?$"
        for i in re.findall(pt, text):
            try:
                iseed = json.loads(i)
                if self.node.is_seed(iseed):
                    seeds.append(iseed)
            except Exception as e:
                pass  # print(e)
        return seeds

    def ingroup(self, group_id: str) -> Dict:
        """search seeds from group"""
        rlt = {}
        for trxdata in self.group.content(group_id):
            iseeds = self.intrx(trxdata)
            for iseed in iseeds:
                if iseed["group_id"] not in rlt:
                    rlt[iseed["group_id"]] = iseed
        if group_id not in rlt:
            rlt[group_id] = self.group.seed(group_id)
        return rlt

    def innode(self) -> Dict:
        rlt = {}
        for group_id in self.node.groups_id:
            rlt.update(self.ingroup(group_id))
        return rlt

    def search_seeds(self, data={}):
        """从已加入的种子网络中搜索新的种子，并更新数据文件"""

        seeds = self.innode()  # 搜寻到的所有种子
        joined = self.node.groups_id  # 已经加入的种子网络

        # 把种子写入数据文件
        for group_id in seeds:
            if group_id not in data:
                data[group_id] = {
                    "seed": seeds[group_id],
                    "is_joined": 0,
                    "is_worth": 1,
                    "memo": "",
                    "create_at": str(datetime.datetime.now()),
                    "update_at": str(datetime.datetime.now()),
                }

        # 自己已经加入的种子网络，更新一下数据文件
        for group_id in joined:
            data[group_id].update(
                {
                    "is_joined": 1,
                    "is_worth": 1,
                    "update_at": str(datetime.datetime.now()),
                }
            )

        # 数据文件中标记为已加入，但实际上未加入的，更新一下（比如已经离开但数据文件未更新）
        for group_id in data:
            if data[group_id]["is_joined"] and group_id not in joined:
                data[group_id].update(
                    {
                        "is_joined": 0,
                        "is_worth": 0,
                        "update_at": str(datetime.datetime.now()),
                    }
                )
        return data

    def leave_group(self, data: Dict, toleave_groupnames: List, is_block=False) -> Dict:
        # 离开满足某些条件的组
        for group_id in self.node.groups_id:
            flag = False
            info = self.group.info(group_id)
            # 退出本人创建的测试组

            if self.group.is_mygroup(group_id):  # 是本人创建的
                if info.group_name in toleave_groupnames:  # 名字在上述列表中
                    flag = True

            # 退出区块数为 0 的 group
            if is_block and info.highest_height == 0:
                flag = True

            if flag:
                resp = self.group.leave(group_id)
                if "group_id" in resp:
                    data[group_id].update(
                        {
                            "is_joined": 0,
                            "is_worth": 0,
                            "update_at": str(datetime.datetime.now()),
                        }
                    )
        return data

    def join_group(self, data):
        for group_id in data:
            if not data[group_id]["is_joined"] and data[group_id]["is_worth"]:
                resp = self.node.join_group(data[group_id]["seed"])
                if "group_id" in resp:
                    data[group_id].update(
                        {
                            "is_joined": 1,
                            "update_at": str(datetime.datetime.now()),
                        }
                    )
        return data

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
