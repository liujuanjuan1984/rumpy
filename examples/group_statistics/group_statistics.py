import datetime
import io
import os
import sys
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import MultipleLocator
from officy import JsonFile
from pylab import *

from rumpy import FullNode
from rumpy.utils import timestamp_to_datetime


class GroupStatistics(FullNode):
    def _count_trxtype(self, trxs):
        rlt = {}
        for i in trxs:
            ix = self.group.trx_type(i)
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

    def _count_daily_trxs(self, trxs):
        rlt = {}
        for i in trxs:
            ix = timestamp_to_datetime(i.get("TimeStamp")).date()
            if ix not in rlt:
                rlt[ix] = 1
            else:
                rlt[ix] += 1
        return rlt

    def _count_daily_pubkeys(self, trxs):
        rlt = {}
        for i in trxs:
            ix = timestamp_to_datetime(i.get("TimeStamp")).date()
            iy = i["Publisher"]

            if ix not in rlt:
                rlt[ix] = [iy]
            elif iy not in rlt[ix]:
                rlt[ix].append(iy)
        return rlt

    def group_view(self, group_id):
        self.group_id = group_id
        trxs = self.group.all_content_trxs()
        info = self.group.info()

        if len(trxs) == 0:
            return {}, 0

        create_at = timestamp_to_datetime(trxs[0].get("TimeStamp"))
        update_at = timestamp_to_datetime(trxs[-1].get("TimeStamp"))
        days = (update_at - create_at).days or 0
        viewdata = {
            "info": info.__dict__,
            "create_at": f"{create_at}",
            "update_at": f"{update_at}",
            "trxtype": self._count_trxtype(trxs),
            "pubkeys": self._count_pubkey(trxs),
            "daily_trxs": self._count_daily_trxs(trxs),
            "daily_pubkeys": self._count_daily_pubkeys(trxs),
        }
        return viewdata, days

    def view_to_save(self, group_id, filepath, imgpath=None):
        data, days = self.group_view(group_id)

        # 数据存入 json 文件。把 datetime 数据类型转换为字符串，才能写入 json 文件
        data["daily_trxs"] = {str(k): data["daily_trxs"][k] for k in data["daily_trxs"]}
        data["daily_pubkeys"] = {str(k): data["daily_pubkeys"][k] for k in data["daily_pubkeys"]}
        JsonFile(filepath).write(data)

        # 绘图
        title = f"{data['info']['group_name']} Daily Trxs and Users Counts"
        daily_trxs = data["daily_trxs"]
        daily_pubkeys = {i: len(data["daily_pubkeys"][i]) for i in data["daily_pubkeys"]}
        imgbytes = self.plot_lines(days, title, daily_trxs, daily_pubkeys)
        imgpath = imgpath or filepath.replace(".json", ".png")

        with open(imgpath, "wb") as f:
            f.write(imgbytes)

    def plot_lines(self, days, title, *data):
        mpl.rcParams["font.sans-serif"] = ["SimHei"]  # 指定默认字体
        mpl.rcParams["axes.unicode_minus"] = False  # 解决保存图像是负号'-'显示为方块的问题
        plt.tick_params(axis="x", labelsize=10)  # 设置x轴字号大小

        for idata in data:
            n = max((days // 10), 1)
            ax = pd.Series(idata).plot(figsize=(15, 8), title=title)
            ax.xaxis.set_major_locator(MultipleLocator(n))  # 设置x轴的间隔为7
            fig = ax.get_figure()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")  # 把数据写入字节流
        imgbytes = buffer.getvalue()
        plt.close(fig)
        return imgbytes

    def view_to_post(self, toview_group_id, toshare_group_id=None):
        data, days = self.group_view(toview_group_id)

        # 绘图
        title = f"{data['info']['group_name']} Daily Trxs and Users Counts"
        daily_trxs = data["daily_trxs"]
        daily_pubkeys = {i: len(data["daily_pubkeys"][i]) for i in data["daily_pubkeys"]}
        imgbytes = self.plot_lines(days, title, daily_trxs, daily_pubkeys)

        # 文本
        note = f"""【{data['info']['group_name']}】数据概况\n创建 {data['create_at']}\n更新 {data['update_at']}\n区块 {data['info']['highest_height']} Trxs {sum(list(data['trxtype'].values()))} 用户 {len(data['pubkeys'])}"""

        # 推送结果到指定组
        kwargs = {"content": note, "images": [imgbytes]}
        toshare_group_id = toshare_group_id or toview_group_id
        self.group_id = toshare_group_id
        return self.group.send_note(**kwargs)
