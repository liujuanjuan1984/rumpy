# -*- coding: utf-8 -*-

import datetime
from typing import List, Dict
import json
import os
import sys
from rumpy import RumClient
from examples.export_data.export_data import trx_export


class WhoSays(RumClient):
    """Rum 产品想法：筛选某人所说，并转发到指定组"""

    def _content_by(self, group_id, pubkeys):
        trxs = self.content(group_id)
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        content_by = [trx_export(i, trxs) for i in trxs_by]
        return content_by

    def search(self, names_info, data):
        for group_id in names_info:
            if group_id not in data:
                data[group_id] = {"seed": self.group.seed(group_id), "trxs": {}}
            # 筛选此人发布的内容
            content_by = self._content_by(group_id, names_info[group_id])
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

                if "trx_id" in self.group.send_note(toshare_group_id, **obj):
                    data[group_id]["trxs"][trx_id]["shared"].append(toshare_group_id)

            return data

    def _quote_text(self, text):
        return "".join(["> ", "\n> ".join(text.split("\n")), "\n"])

    def _trans(self, one):
        obj = {"image": []}
        lines = []
        _info = {"like": "赞", "dislike": "踩"}
        t = one["trx_type"]
        if t in _info:
            name = one["refer_to"]["name"] or "某人"
            lines.append(f"点{_info[t]}给 `{name}` 发布的内容。")
            if "text" in one["refer_to"]:
                lines.append(self._quote_text(one["refer_to"]["text"]))
            if "imgs" in one["refer_to"]:
                obj["image"].extend(one["refer_to"]["imgs"])

        elif t == "person":
            lines.append(f"修改了个人信息。")
        elif t == "annouce":
            lines.append(f"处理了链上请求。")
        elif t == "reply":
            lines.append(f"回复说：")
            if "text" in one:
                lines.append(f"{one['text']}")
            if "imgs" in one:
                obj["image"].extend(one["refer_to"]["imgs"])

            name = one["refer_to"]["name"] or "某人"

            lines.append(f"\n回复给 `{name}` 所发布的内容：")
            if "text" in one["refer_to"]:
                lines.append(self._quote_text(one["refer_to"]["text"]))
            if "imgs" in one["refer_to"]:
                obj["image"].extend(one["refer_to"]["imgs"])

        else:
            lines.append("说：")
            if "text" in one:
                lines.append(one["text"])
            if "imgs" in one:
                obj["image"].extend(one["imgs"])
        obj["content"] = one["trx_time"] + " " + "\n".join(lines)
        return obj
