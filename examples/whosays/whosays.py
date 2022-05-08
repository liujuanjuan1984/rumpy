import datetime
import json
import os
from typing import List, Dict
from officy import JsonFile, Dir, Stime
from rumpy import RumClient
from examples.users_profiles.users_profiles import update_profiles


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
        Dir(datadir).check()
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

    def send(self, name: str, toshare_group_id: str) -> Dict:
        """发布内容并更新发布状态"""
        data = JsonFile(self.trxs_file).read({})
        for group_id in data:
            gtrxs = data[group_id]
            self.group_id = group_id
            if not self.group.is_joined():
                continue
            nicknames = (
                update_profiles(self, users_profiles_dir=self.datadir, profile_types=("name",)).get("data") or {}
            )
            for trx_id in gtrxs:
                self.group_id = group_id
                if "shared" not in gtrxs[trx_id]:
                    data[group_id][trx_id]["shared"] = []
                if toshare_group_id in data[group_id][trx_id]["shared"]:
                    continue
                obj, can_post = self.trx_to_newobj(gtrxs[trx_id], nicknames)
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

    def _quote(self, text):
        return "".join(["> ", "\n> ".join(text.split("\n")), "\n"]) if text else ""

    def _nickname(self, pubkey, nicknames):
        try:
            name = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})"
        except:
            name = pubkey[-10:-2] or "某人"
        return name

    def trx_to_newobj(self, trx, nicknames):
        """trans from trx to an object of new trx to send to chain.

        Args:
            trx (dict): the trx data
            nicknames (dict): the nicknames data of the group

        Returns:
            obj: object of NewTrx,can be used as: client.group.send_note(obj=obj).
            result: True,or False, if True, the obj can be send to chain.
        """

        if "Content" not in trx:
            return None, False

        obj = {"type": "Note", "image": []}
        ttype = trx["TypeUrl"]
        tcontent = trx["Content"]
        lines = []

        if ttype == "quorum.pb.Person":
            _name = "昵称" if "name" in tcontent else ""
            _wallet = "钱包" if "wallet" in tcontent else ""
            _image = "头像" if "image" in tcontent else ""
            _profile = "、".join([i for i in [_name, _image, _wallet] if i])
            lines.append(f"修改了个人信息：{_profile}。")
        elif ttype == "quorum.pb.Object":
            if tcontent.get("type") == "File":
                lines.append(f"上传了文件。")
            else:
                text = trx["Content"].get("content") or ""
                img = trx["Content"].get("image") or []
                lines.append(text)
                obj["image"].extend(img)

                t = self.group.trx_type(trx)
                refer_tid = None
                _info = {"like": "赞", "dislike": "踩"}
                if t == "announce":
                    lines.insert(0, f"处理了链上请求。")
                elif t in _info:
                    refer_tid = trx["Content"]["id"]
                    refer_pubkey = self.group.trx(refer_tid).get("Publisher") or ""
                    lines.insert(0, f"点{_info[t]}给 `{self._nickname( refer_pubkey,nicknames)}` 所发布的内容：")
                elif t == "reply":
                    lines.insert(0, f"回复说：")
                    refer_tid = trx["Content"]["inreplyto"]["trxid"]
                    refer_pubkey = self.group.trx(refer_tid).get("Publisher") or ""
                    lines.append(f"\n回复给 `{self._nickname(refer_pubkey,nicknames)}` 所发布的内容：")
                else:
                    lines.insert(0, f"说：")

                if refer_tid:
                    refer_trx = self.group.trx(refer_tid)
                    refer_text = refer_trx["Content"].get("content") or ""
                    refer_img = refer_trx["Content"].get("image") or []
                    lines.append(self._quote(refer_text))
                    obj["image"].extend(refer_img)
        else:
            print(trx)
            return None, False

        obj["content"] = f'{Stime.ts2datetime(trx.get("TimeStamp"))}' + " " + "\n".join(lines)
        obj["image"] = obj["image"][:4]
        obj = {key: obj[key] for key in obj if obj[key]}

        return obj, True
