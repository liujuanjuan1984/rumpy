# -*- coding: utf-8 -*-

import datetime
import dataclasses
import json
import os
import re
import sys

sys.path.append(os.path.realpath("."))
from rumpy import RumClient, JsonFile
from rumpy.client.api.node import Seed


class SearchSeeds(RumClient):
    def _content(self, trxdata):
        try:
            return trxdata["Content"]["content"]
        except:
            return ""

    def _search_seeds(self, trxdata):
        text = self._content(trxdata).replace("\n", " ")

        if text == "":
            return []

        # 包含 Seed 的所有字段
        for f in dataclasses.fields(Seed):
            if f.name not in text:
                return []

        # 只能识别单个种子
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

    def search_seeds(self, filepath):
        data = JsonFile(filepath).read()
        joined = self.node.groups_id

        # 自己已经加入的种子网络
        for group_id in joined:
            if group_id not in data:
                data[group_id] = {
                    "seed": self.group.seed(group_id),
                    "is_joined": 1,
                    "is_worth": 1,
                    "memo": "",
                    "create_at": str(datetime.datetime.now()),
                    "update_at": str(datetime.datetime.now()),
                }

        # 通过已经加入的种子网络，来搜寻更多种子网络
        for group_id in joined:
            for trxdata in self.group.content(group_id):
                seeds = self._search_seeds(trxdata)
                for seed in seeds:
                    if seed["group_id"] not in data:
                        data[seed["group_id"]] = {
                            "seed": seed,
                            "is_joined": 0,
                            "is_worth": 1,
                            "memo": "",
                            "create_at": str(datetime.datetime.now()),
                            "update_at": str(datetime.datetime.now()),
                        }

        JsonFile(filepath).write(data)
        return data

    def leave_group(self, filepath, toleave_groupnames, is_block=False):
        # 离开满足某些条件的组
        data = JsonFile(filepath).read()
        joined = self.node.groups_id

        for group_id in joined:
            info = self.group.info(group_id)

            flag = False
            # 退出本人创建的测试组
            if self.group.is_mygroup(group_id):  # 是本人创建的
                if info.group_name in toleave_groupnames:  # 名字在上述列表中
                    flag = True

            # 退出区块数为 0 的 group
            if is_block and info.highest_height == 0:
                flag = True

            if flag:
                self.group.leave(group_id)
                data[group_id]["is_worth"] = 0
                data[group_id]["is_joined"] = 0
                data[group_id]["update_at"] = str(datetime.datetime.now())

        JsonFile(filepath).write(data)
        return data

    def join_group(self, filepath):
        data = JsonFile(filepath).read()
        joined = self.node.groups_id
        for group_id in data:
            if data[group_id]["is_joined"] == 0 and data[group_id]["is_worth"] == 1:
                self.node.join_group(data[group_id]["seed"])
                data[group_id]["is_joined"] = 1
                data[group_id]["update_at"] = str(datetime.datetime.now())

        JsonFile(filepath).write(data)
        return data
