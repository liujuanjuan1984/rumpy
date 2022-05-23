import json
import os
from typing import Dict, List

from officy import JsonFile

from rumpy import RumClient


class WhoSays(RumClient):
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
        if not os.path.exists(datadir):
            os.makedirs(datadir)

        namesinfofile = os.path.join(datadir, "names_info.json")
        self.datadir = datadir
        self.trxs_file = os.path.join(datadir, "whosays_trxs.json")
        self.progressfile = os.path.join(datadir, "progress.json")
        self.names_info = JsonFile(namesinfofile).read({})

    def search(self):
        data = JsonFile(self.trxs_file).read({})
        progress = JsonFile(self.progressfile).read({})

        if not self.names_info:
            raise ValueError("add data in names_info file with data like {group_id:[pubkey]}")

        for group_id in self.names_info:
            pubkeys = [k for k in self.names_info[group_id]]

            if len(pubkeys) == 0:
                continue

            self.group_id = group_id

            if group_id not in data:
                data[group_id] = {}

            if group_id not in progress:
                progress[group_id] = None

            trxs = self.group.all_content_trxs(senders=pubkeys, trx_id=progress[group_id])
            for trx in trxs:
                if trx["Publisher"] not in pubkeys:
                    print("ERROR: all_content_trxs senders params must be wrong.")
                    continue

                if trx["TrxId"] not in data[group_id]:
                    data[group_id][trx["TrxId"]] = trx

            progress[group_id] = self.group.last_trx_id(progress[group_id], trxs)
            JsonFile(self.trxs_file).write(data)
            JsonFile(self.progressfile).write(progress)

    def group_update_profiles(
        self,
        group_id,
        datadir,
        types=("name", "wallet", "image"),
    ):
        self.group_id = group_id
        filename = f"users_profiles_group_{self.group_id}.json"
        users_profiles_file = os.path.join(datadir, filename)
        users_data = JsonFile(users_profiles_file).read({})
        users_data = self.group.get_users_profiles(users_data, types)
        JsonFile(users_profiles_file).write(users_data)
        return users_data

    def send(self, name: str, toshare_group_id: str) -> Dict:
        """发布内容并更新发布状态"""
        data = JsonFile(self.trxs_file).read({})
        for group_id in data:
            gtrxs = data[group_id]
            self.group_id = group_id
            if not self.group.is_joined():
                continue
            _params = {
                "group_id": group_id,
                "datadir": self.datadir,
                "types": ("name",),
            }
            _profiles = self.group_update_profiles(**_params)
            nicknames = _profiles.get("data", {})
            for trx_id in gtrxs:
                self.group_id = group_id
                if "shared" not in gtrxs[trx_id]:
                    data[group_id][trx_id]["shared"] = []
                if toshare_group_id in data[group_id][trx_id]["shared"]:
                    continue
                obj, can_post = self.group.trx_to_newobj(gtrxs[trx_id], nicknames)
                if not can_post:
                    continue
                _seed = json.dumps(self.group.seed())
                _origin = f"origin: {_seed}" if _seed else f"origin: Group {group_id}"
                obj["content"] = f"{name} {obj['content']}\n{_origin}"
                self.group_id = toshare_group_id
                resp = self.group.send_note(obj=obj)

                if "trx_id" in resp:
                    data[group_id][trx_id]["shared"].append(toshare_group_id)
                    JsonFile(self.trxs_file).write(data)
                else:
                    print(resp)
