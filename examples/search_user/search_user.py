import datetime
import os
import random
from typing import Dict, List
from officepy import JsonFile
from rumpy import RumClient


class SearchUser(RumClient):
    """bot:search pubkeys in all-history-nicknames for those containing with the piece: name_fragment"""

    def init(self, name_fragment):
        if type(name_fragment) != str:
            raise TypeError("param:name_fragment type error. It should be string.")
        if len(name_fragment) < 2:
            raise ValueError("param:name_fragment too short! Give something to search.")

        self.name_fragment = name_fragment.lower()
        this_dir = os.path.dirname(__file__)
        self.rltfile = os.path.join(
            this_dir, "data", f"search_user_{name_fragment}.json"
        )
        self.seedsfile = os.path.join(this_dir, "data", f"seeds.json")
        self.progressfile = os.path.join(
            this_dir, "data", f"search_user_{name_fragment}_progress.json"
        )
        JsonFile(self.rltfile).rewrite({})
        JsonFile(self.seedsfile).rewrite({})
        JsonFile(self.progressfile).rewrite({})

    def _intrx(self, trx: Dict):
        """
        returns:pubkey,nickname
        """

        if trx["TypeUrl"] == "quorum.pb.Person":
            name = trx["Content"].get("name") or ""
            if name.lower().find(self.name_fragment) >= 0:
                return trx["Publisher"], name
        return None, None

    def _ingroup(self, trx_id=None, group_rlt=None):
        """
        search in group from the trx_id.
        default to be None.
        which means searching from the beginning.

        returns:
        group_rlt: {pubkey:[nickname1,nickname2]}
        progress:trx_id

        """
        group_rlt = group_rlt or {}
        trxids_searched = []

        while True:
            print(datetime.datetime.now(), self.name_fragment, trx_id, "...")
            trxs = self.group.content_trxs(num=400, trx_id=trx_id)

            if len(trxs) == 0:
                break

            for trx in trxs:
                pubkey, name = self._intrx(trx)
                if not pubkey:
                    continue
                if pubkey not in group_rlt:
                    group_rlt[pubkey] = [name]
                if name not in group_rlt[pubkey]:
                    group_rlt[pubkey].append(name)

            if trx_id not in trxids_searched:
                trxids_searched.append(trx_id)

            for i in range(-1, -1 * len(trxs), -1):
                new_trxid = trxs[i]["TrxId"]
                if new_trxid in trxids_searched:
                    continue
                else:
                    trx_id = new_trxid
                    break
            if trx_id in trxids_searched:
                break

        return trx_id, group_rlt

    def innode(self):
        """
        返回
        rlt: {group_id : {pubkey:[name,name]}}#pubkey及包含该昵称片段的昵称全称
        seeds: {group_id:seed}  #方便其它bot直接加入
        progress: {group_id:trx_id} #已搜索至的 trx_id
        """
        rlt = JsonFile(self.rltfile).read({})
        seeds = JsonFile(self.seedsfile).read({})
        progress = JsonFile(self.progressfile).read({})

        for group_id in self.node.groups_id:
            self.group_id = group_id
            print(datetime.datetime.now(), group_id, self.name_fragment, "searching...")

            if group_id not in rlt:
                rlt[group_id] = {}
            if group_id not in seeds:
                seed = self.group.seed(group_id)
                if "error" not in seed and not seed["group_name"].startswith("mytest_"):
                    seeds[group_id] = seed
            if group_id not in progress:
                progress[group_id] = None

            trx_id, group_rlt = self._ingroup(progress[group_id], rlt[group_id])
            progress[group_id] = trx_id

            for pubkey in group_rlt:
                if pubkey not in rlt[group_id]:
                    rlt[group_id][pubkey] = group_rlt[pubkey]
                else:
                    for nickname in group_rlt[pubkey]:
                        if nickname not in rlt[group_id][pubkey]:
                            rlt[group_id][pubkey].append(nickname)

        JsonFile(self.progressfile).write(progress)
        JsonFile(self.rltfile).write(rlt)
        JsonFile(self.seedsfile).write(seeds)
