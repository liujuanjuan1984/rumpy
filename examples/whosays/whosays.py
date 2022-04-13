import datetime
import json
import os
from typing import List, Dict
from officy import JsonFile, Dir, Stime
from rumpy import RumClient


class WhoSays(RumClient):
    """
    bot: got what who says and retweet to the group.
    在多个组内筛选某人动态，并转发到指定组。
    """

    def init(self, dirname, seedsfile=None):
        """
        names_info:
        {group_id:[pubkey1,pubkey2]}
        data:

        """
        datadir = os.path.join(os.path.dirname(__file__), "data", dirname)
        Dir(datadir).check()
        namesinfofile = os.path.join(datadir, "names_info.json")
        self.datafile = os.path.join(datadir, "whosays_trxs.json")
        self.progressfile = os.path.join(datadir, "progress.json")
        self.seedsfile = seedsfile or os.path.join(datadir, "seeds.json")
        self.nicknamesfile = os.path.join(datadir, "nicknames.json")
        JsonFile(namesinfofile).rewrite({})
        JsonFile(self.datafile).rewrite({})
        JsonFile(self.progressfile).rewrite({})
        JsonFile(self.seedsfile).rewrite({})
        JsonFile(self.nicknamesfile).rewrite({})
        self.names_info = JsonFile(namesinfofile).read({})

    def search(self):
        data = JsonFile(self.datafile).read({})
        seeds = JsonFile(self.seedsfile).read({})
        progress = JsonFile(self.progressfile).read({})

        if not self.names_info:
            raise ValueError("add data in names_info file with data like {group_id:[pubkey]}")

        for group_id in self.names_info:
            self.group_id = group_id

            if group_id not in data:
                data[group_id] = {}
            if group_id not in seeds:
                seed = self.group.seed()
                if seed:
                    seeds[group_id] = seed
            if group_id not in progress:
                progress[group_id] = None
            pubkeys = self.names_info[group_id]

            trxs = self.group.all_content_trxs(senders=pubkeys, trx_id=progress[group_id])

            for trx in trxs:
                if trx["TrxId"] not in data[group_id]:
                    data[group_id][trx["TrxId"]] = trx

            progress[group_id] = self.group.last_trx_id(progress[group_id], trxs)
            JsonFile(self.datafile).write(data)
            JsonFile(self.progressfile).write(progress)
            JsonFile(self.seedsfile).write(seeds)

    def send(self, name: str, toshare_group_id: str) -> Dict:
        """发布内容并更新发布状态"""
        data = JsonFile(self.datafile).read({})
        seeds = JsonFile(self.seedsfile).read({})
        for group_id in data:
            gtrxs = data[group_id]
            seed = seeds.get(group_id) or {}
            if not seed:
                continue
            self.group_id = group_id
            for trx_id in gtrxs:
                if "shared" not in gtrxs[trx_id]:
                    data[group_id][trx_id]["shared"] = []
                if toshare_group_id in data[group_id][trx_id]["shared"]:
                    continue
                obj, flag = self._trans(gtrxs[trx_id])
                if not flag:
                    continue
                obj["content"] = f"{name} {obj['content']}\norigin: {json.dumps(seed)}"
                self.group_id = toshare_group_id
                resp = self.group.send_note(**obj)

                if "trx_id" in resp:
                    data[group_id][trx_id]["shared"].append(toshare_group_id)
                    JsonFile(self.datafile).write(data)

    def _quote_text(self, text):
        return "".join(["> ", "\n> ".join(text.split("\n")), "\n"])

    def _nickname(self, pubkey):
        names = JsonFile(self.nicknamesfile).read({})
        if pubkey not in names:
            names[pubkey] = {
                "pubkey": pubkey,
                "group_id": self.group_id,
                "nicknames": ["某人"],
                "trx_id": None,
            }

        if self.group_id != names[pubkey]["group_id"]:
            raise ValueError(f"group_id error. check it.{self.group_id},{names[pubkey]['group_id']}")

        searched_trxids = []
        while True:
            trx_id = names[pubkey]["trx_id"]
            if trx_id in searched_trxids:
                break
            else:
                searched_trxids.append(trx_id)
            print(datetime.datetime.now(), "_nickname", trx_id, "...")
            trxs = self.group.content_trxs(num=400, trx_id=trx_id)
            if len(trxs) == 0:
                break
            for trx in trxs:
                if trx["Publisher"] != pubkey:
                    continue
                if trx["TypeUrl"] == "quorum.pb.Person":
                    name = trx["Content"].get("name") or ""
                    if name not in names[pubkey]["nicknames"]:
                        names[pubkey]["nicknames"].append(name)
            names[pubkey]["trx_id"] = trxs[-1]["TrxId"]

        JsonFile(self.nicknamesfile).write(names)
        return names[pubkey]["nicknames"][-1]

    def _name(self, trx_id):
        return self._nickname(self.group.trx(trx_id).get("Publisher"))

    def _refer_content(self, trx):
        if type(trx) == str:
            trx = self.group.trx(trx)
        text, img = None, None
        if "Content" not in trx:
            return text, img, text or img
        if "content" in trx["Content"]:
            text = trx["Content"]["content"]
        if "image" in trx["Content"]:
            if type(trx["Content"]["image"]) == dict:
                img = [trx["Content"]["image"]]
            else:
                img = trx["Content"]["image"]

        return text, img, text or img

    def _trans(self, trx):
        obj = {"image": []}
        lines = []
        flag = False
        t = self.group.trx_type(trx)
        _info = {"like": "赞", "dislike": "踩"}
        if t in _info:
            trxid = trx["Content"]["id"]
            lines.append(f"点{_info[t]}给 `{self._name(trxid)}` 发布的内容。")
            text, img, flag = self._refer_content(trxid)
            if text:
                lines.append(self._quote_text(text))
            if img:
                obj["image"].extend(img)

        elif t == "person":
            lines.append(f"修改了个人信息。")
        elif t == "annouce":
            lines.append(f"处理了链上请求。")
        elif t == "reply":
            lines.append(f"回复说：")
            text, img, flag = self._refer_content(trx["TrxId"])
            if text:
                lines.append(self._quote_text(text))
            if img:
                obj["image"].extend(img)
            trxid = trx["Content"]["inreplyto"]["trxid"]
            lines.append(f"回复给 `{self._name(trxid)}` 所发布的内容：")
            text, img, flag = self._refer_content(trxid)
            if text:
                lines.append(self._quote_text(text))
            if img:
                obj["image"].extend(img)
        else:
            lines.append("说：")
            text, img, flag = self._refer_content(trx["TrxId"])
            if text:
                lines.append(self._quote_text(text))
            if img:
                obj["image"].extend(img)
        obj["content"] = f'{Stime.ts2datetime(trx.get("TimeStamp"))}' + " " + "\n".join(lines)
        return obj, flag
