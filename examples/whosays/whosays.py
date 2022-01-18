# -*- coding: utf-8 -*-

import datetime
from typing import List, Dict
import json
from time import sleep
import os
import sys

sys.path.append(os.path.realpath("."))
from rumpy import RumClient


class WhoSays(RumClient):
    """Rum 产品想法：筛选某人所说，并转发到指定组"""

    def search(self, names_info, data):
        for group_id in names_info:
            if group_id not in data:
                data[group_id] = {"seed": self.group.seed(group_id), "trxs": {}}
            # 筛选此人发布的内容
            content_by = self.group.content_by(group_id, names_info[group_id])
            for ic in content_by:
                if ic["trx_id"] not in data[group_id]["trxs"]:
                    data[group_id]["trxs"][ic["trx_id"]] = ic
        return data

    def send(self, name: str, toshare_group_id: str, data: Dict) -> Dict:
        """发布内容并更新发布状态"""
        for group_id in data:
            gtrxs = data[group_id]["trxs"]
            seed = data[group_id]["seed"]
            for trx_id in gtrxs:
                if "shared" not in gtrxs[trx_id]:
                    data[group_id]["trxs"][trx_id]["shared"] = []
                if toshare_group_id in data[group_id]["trxs"][trx_id]["shared"]:
                    continue
                obj = self._trans(gtrxs[trx_id])
                obj["content"] = f"{name} {obj['content']}来源{json.dumps(seed)}"

                resp = self.group.send_note(toshare_group_id, **obj)
                if "error" not in resp:
                    data[group_id]["trxs"][trx_id]["shared"].append(toshare_group_id)
                else:
                    print(resp, obj)
            return data

    def _trans(self, one):
        obj = {"image": []}
        note = f'{one["trx_time"]} '
        _info = {"like": "赞", "dislike": "踩"}
        t = one["trx_type"]
        if t in _info:
            name = one["refer_to"]["name"] or "某人"
            note = f"{note}点{_info[t]}给 `{name}` 发布的内容。\n"
            if "text" in one["refer_to"]:
                note = f'{note}> {"\n> ".join(one["refer_to"]["text"].split("\n"))}\n'
            if "imgs" in one["refer_to"]:
                obj["image"].extend(one["refer_to"]["imgs"])

        elif t == "person":
            note = f"{note}修改了个人信息。\n"
        elif t == "annouce":
            note  = f"{note}处理了链上请求。\n"
        elif t == "reply":
            note  = f"{note}回复说：\n"
            if "text" in one:
                note = f'{note}{one["text"]}\n'
            if "imgs" in one:
                obj["image"].extend(one["refer_to"]["imgs"])

            name = one["refer_to"]["name"] or "某人"
            note  = f"{note}\n回复给 `{name}` 所发布的内容：\n"
            if "text" in one["refer_to"]:
                note = f'{note}> {"\n> ".join(one["refer_to"]["text"].split("\n"))}\n'
            if "imgs" in one["refer_to"]:
                obj["image"].extend(one["refer_to"]["imgs"])

        else:
            note = f"{note}说：\n"
            if "text" in one:
                note = f'{note}{one["text"]}\n'
            if "imgs" in one:
                obj["image"].extend(one["imgs"])
        obj["content"] = note
        return obj
