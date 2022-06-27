import datetime
import io
import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import MultipleLocator
from officy import JsonFile
from pylab import *

import rumpy.utils as utils
from rumpy.exceptions import ParamValueError

logger = logging.getLogger(__name__)


class GroupStatistics:
    """
    A tool to do Group Statistics and post the result to the group.
    - group_view: 统计指定组的数据
    - view_to_post: 生成统计文本、趋势图；可以选择是否发布到指定组；也可以保存到本地
    """

    def __init__(self, rum_client):
        self.rum = rum_client

    def group_view(self, group_id):

        trxs = self.rum.api.get_group_all_contents(group_id=group_id, num=200)
        info = self.rum.api.group_info(group_id)

        create_at = update_at = None
        trxtypes = {}
        pubkeys = {}
        dailytrxs = {}
        dailypubkeys = {}
        for trx in trxs:
            dt = utils.trx_ts(trx, "datetime")
            if create_at is None:
                create_at = dt
            if update_at is None:
                update_at = dt
            if create_at and dt < create_at:
                create_at = dt
            if update_at and dt > update_at:
                update_at = dt
            itype = utils.trx_type(trx)
            trxtypes[itype] = trxtypes.get(itype, 0) + 1
            ipubkey = trx.get("Publisher", "error")
            pubkeys[ipubkey] = pubkeys.get(ipubkey, 0) + 1
            iday = str(dt.date())
            dailytrxs[iday] = dailytrxs.get(iday, 0) + 1
            if iday not in dailypubkeys:
                dailypubkeys[iday] = []
            if ipubkey not in dailypubkeys[iday]:
                dailypubkeys[iday].append(ipubkey)

        viewdata = {
            "info": info.__dict__,
            "create_at": create_at,
            "update_at": update_at,
            "trxtype": trxtypes,
            "pubkeys": pubkeys,
            "daily_trxs": dailytrxs,
            "daily_pubkeys": dailypubkeys,
        }
        return viewdata

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

    def view_to_post(
        self,
        toview_group_id,
        toshare_group_id=None,
        send_to_group=True,
        save_to_dir=None,
    ):
        """
        Args:
            toview_group_id (_type_): _description_
            toshare_group_id (_type_, optional): _description_. Defaults to None.
            send_to_group (bool, optional): 是否把统计数据及趋势图发送到 rum group. Defaults to True. 如果没有指定 toshare_group_id，将默认发送到 toview_group_id。
            save_to_dir (_type_, optional): 统计数据及趋势图保存到 json 数据文件，以供更多自定义处理. Defaults to None.
        """
        data = self.group_view(toview_group_id)
        try:
            days = (data["update_at"] - data["create_at"]).days
        except TypeError as e:
            raise ParamValueError(403, f"{e}")
        if days < 3:
            raise ParamValueError(403, f"only got {days} days data, too few to draw pictures.")

        # 绘图
        title = f"{data['info']['group_name']} Daily Trxs and Users Counts"
        daily_trxs = data["daily_trxs"]
        daily_pubkeys = {i: len(data["daily_pubkeys"][i]) for i in data["daily_pubkeys"]}
        imgbytes = self.plot_lines(days, title, daily_trxs, daily_pubkeys)

        # 推送结果到指定组
        if send_to_group:
            # 文本
            note = f"""【{data['info']['group_name']}】数据概况\n创建 {data['create_at']}\n更新 {data['update_at']}\n区块 {data['info']['highest_height']} Trxs {sum(list(data['trxtype'].values()))} 用户 {len(data['pubkeys'])}"""
            toshare_group_id = toshare_group_id or toview_group_id
            self.rum.api.send_note(group_id=toshare_group_id, content=note, images=[imgbytes])

        if save_to_dir:
            utils.check_dir(save_to_dir)
            _today = datetime.date.today()
            datafile = os.path.join(
                save_to_dir,
                f"group_statistics_group{toview_group_id}_{_today}.json",
            )
            imgfile = os.path.join(
                save_to_dir,
                f"group_statistics_group{toview_group_id}_{_today}.png",
            )
            JsonFile(datafile).write(data)
            with open(imgfile, "wb") as f:
                f.write(imgbytes)
        return True
