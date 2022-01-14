# -*- coding: utf-8 -*-

import datetime
from typing import List, Dict
import os
import sys
import pandas as pd

sys.path.append(os.path.realpath("."))
from rumpy import RumClient, JsonFile


class GroupStatistics(RumClient):
    def _count_trxtype(self, trxs):
        rlt = {}
        for i in trxs:
            ix = self.trx.trx_type(i)
            if ix not in rlt:
                rlt[ix] = 1
            else:
                rlt[ix] += 1
        return rlt

    def _count_pubkey(self, trxs):
        rlt = {}
        for i in trxs:
            ix = i["Publisher"]
            if ix not in rlt:
                rlt[ix] = 1
            else:
                rlt[ix] += 1
        return rlt

    def _ts(self, ts):
        return datetime.datetime.fromtimestamp(int(ts / 1000000000))

    def _count_daily_trxs(self, trxs):
        rlt = {}
        for i in trxs:
            ix = self._ts(i["TimeStamp"]).date()
            if ix not in rlt:
                rlt[ix] = 1
            else:
                rlt[ix] += 1
        return rlt

    def _count_daily_pubkeys(self, trxs):
        rlt = {}
        for i in trxs:
            ix = self._ts(i["TimeStamp"]).date()
            iy = i["Publisher"]

            if ix not in rlt:
                rlt[ix] = [iy]
            elif iy not in rlt[ix]:
                rlt[ix].append(iy)
        return rlt

    def group_view(self, group_id):

        trxs = self.group.content(group_id)
        info = self.group.info(group_id)

        return {
            "info": info.__dict__,
            "create_at": str(self._ts(trxs[0]["TimeStamp"]))[:19],
            "update_at": str(self._ts(trxs[-1]["TimeStamp"]))[:19],
            "trxtype": self._count_trxtype(trxs),
            "pubkeys": self._count_pubkey(trxs),
            "daily_trxs": self._count_daily_trxs(trxs),
            "daily_pubkeys": self._count_daily_pubkeys(trxs),
        }

    def view_to_save(self, group_id, filepath):
        rlt = self.group_view(group_id)
        # 把 datetime 数据类型转换为字符串，才能写入 json 文件
        rlt["daily_trxs"] = {str(k): rlt["daily_trxs"][k] for k in rlt["daily_trxs"]}
        rlt["daily_pubkeys"] = {
            str(k): rlt["daily_pubkeys"][k] for k in rlt["daily_pubkeys"]
        }
        JsonFile(filepath).write(rlt)

    def view_to_post(self, toview_group_id, toshare_group_id=None):
        data = self.group_view(toview_group_id)

        k = max(data["pubkeys"].values())
        # pubkeys = [i for i in data['pubkeys'] if data['pubkeys'][i] == k]

        note = f"""【{data['info']['group_name']}】数据概况\n创建 {data['create_at']}\n更新 {data['update_at']}\n区块 {data['info']['highest_height']} Trxs {sum(data['trxtype'].values())} 用户 {len(data['pubkeys'])}\n"""

        imgpath1 = "temptemp1.png"
        imgpath2 = "temptemp2.png"
        pd.Series(data["daily_trxs"]).plot(
            figsize=(10, 7), title=f"Daily Trxs Counts", grid=False, stacked=False
        ).get_figure().savefig(imgpath1)

        daily_pubkeys = {}
        for i in data["daily_pubkeys"]:
            daily_pubkeys[i] = len(data["daily_pubkeys"][i])

        pd.Series(daily_pubkeys).plot(
            figsize=(15, 8),
            title=f"Daily Trxs and Users Counts",
            grid=False,
            stacked=False,
        ).get_figure().savefig(imgpath2)

        kwargs = {"content": note, "image": [imgpath2]}
        if toshare_group_id == None:
            toshare_group_id = toview_group_id
        self.group.send_note(toshare_group_id, **kwargs)
