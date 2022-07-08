import json
import os
from typing import Dict, List

from officy import JsonFile

import rumpy.utils as utils
from rumpy import FullNode
from rumpy.exceptions import *


class WhoSays(FullNode):
    """
    bot: got what who says and retweet to the group.
    在多个组内筛选某人动态，并转发到指定组。
    """

    def init(self, dirname):
        """
        names_info:
        {group_id:[pubkey1,pubkey2]}
        data:

        """
        datadir = os.path.join(os.path.dirname(__file__), "data", dirname)
        utils.check_dir(datadir)
        namesinfofile = os.path.join(datadir, "names_info.json")
        self.datadir = datadir
        self.trxs_file = os.path.join(datadir, "whosays_trxs.json")
        self.progressfile = os.path.join(datadir, "progress.json")
        self.names_info = JsonFile(namesinfofile).read({})

    def search(self):
        data = JsonFile(self.trxs_file).read({})
        progress = JsonFile(self.progressfile).read({})

        if not self.names_info:
            raise ParamValueError(
                "add data in names_info file with data like {group_id:[pubkey]}",
            )

        for group_id in self.names_info:
            pubkeys = [k for k in self.names_info[group_id]]

            if len(pubkeys) == 0:
                continue

            if group_id not in data:
                data[group_id] = {}

            if group_id not in progress:
                progress[group_id] = None

            trxs = self.api.get_group_all_contents(group_id=group_id, senders=pubkeys, trx_id=progress[group_id])
            progress_tid = progress[group_id]
            for trx in trxs:
                progress_tid = trx["TrxId"]
                if trx["TrxId"] not in data[group_id]:
                    data[group_id][trx["TrxId"]] = trx

            progress[group_id] = progress_tid
            JsonFile(self.trxs_file).write(data)
            JsonFile(self.progressfile).write(progress)

    def group_update_profiles(
        self,
        group_id,
        datadir,
        types=("name", "wallet", "image"),
    ):
        filename = f"users_profiles_group_{group_id}.json"
        users_profiles_file = os.path.join(datadir, filename)
        users_data = JsonFile(users_profiles_file).read({})
        users_data = self.api.update_profiles_data(group_id=group_id, users_data=users_data, types=types)
        JsonFile(users_profiles_file).write(users_data)
        return users_data

    def send(self, name: str, toshare_group_id: str) -> Dict:
        """发布内容并更新发布状态"""
        data = JsonFile(self.trxs_file).read({})
        for group_id in data:
            gtrxs = data[group_id]
            if not self.api.is_joined(group_id=group_id):
                continue
            _params = {
                "group_id": group_id,
                "datadir": self.datadir,
                "types": ("name",),
            }
            _profiles = self.group_update_profiles(**_params)
            nicknames = _profiles.get("data", {})
            for trx_id in gtrxs:
                if "shared" not in gtrxs[trx_id]:
                    data[group_id][trx_id]["shared"] = []
                if toshare_group_id in data[group_id][trx_id]["shared"]:
                    continue
                params = self.api.trx_retweet_params(group_id=group_id, trx=gtrxs[trx_id], nicknames=nicknames)
                if not params:
                    continue
                _seed = json.dumps(self.api.seed(group_id))
                _origin = f"origin: {_seed}" if _seed else f"origin: Group {group_id}"
                params["content"] = f"{name} {params['content']}\n{_origin}"
                resp = self.api.send_note(group_id=toshare_group_id, **params)

                if "trx_id" in resp:
                    data[group_id][trx_id]["shared"].append(toshare_group_id)
                    JsonFile(self.trxs_file).write(data)
                else:
                    print(resp)
