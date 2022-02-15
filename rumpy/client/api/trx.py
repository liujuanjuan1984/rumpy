# -*- coding: utf-8 -*-

import datetime
import re
import json
import time
from typing import List, Dict
from .base import BaseRumAPI


class RumTrx(BaseRumAPI):
    def info(self, group_id: str, trx_id: str):
        return self._get(f"{self.baseurl}/trx/{group_id}/{trx_id}")

    def trx_type(self, trxdata: Dict):
        """get type of trx, trx is one of group content list"""
        if trxdata["TypeUrl"] == "quorum.pb.Person":
            return "person"
        content = trxdata["Content"]
        trxtype = content.get("type") or "other"
        if type(trxtype) == int:
            return "announce"
        if trxtype == "Note":
            if "inreplyto" in content:
                return "reply"
            if "image" in content:
                if "content" not in content:
                    return "image_only"
                else:
                    return "image_text"
            return "text_only"
        return trxtype.lower()  # "like","dislike","other"

    def trxdata(self, trx_id, trxs):
        for trxdata in trxs:
            if trxdata["TrxId"] == trx_id:
                return trxdata
        return {}

    def trx_text(self, trxdata):
        try:
            text = trxdata["Content"]["content"]
        except:
            text = ""
        return text

    def get_trx_content(self, trxs, trx_id):
        trxdata = self.trxdata(trx_id, trxs)
        text = self.trx_text(trxdata)
        return text

    def person_name(self, trx_id_or_pubkey, trxs, since=None):
        """get the lastest name of the person published the trx_id"""
        key = "SenderPubkey" if "Publisher" not in trxs[0] else "Publisher"
        if trx_id_or_pubkey.endswith("=="):
            pubkey = trx_id_or_pubkey
        else:
            trx_id = trx_id_or_pubkey
            trxdata = self.trxdata(trx_id, trxs)
            pubkey = trxdata[key]

        rlt = []
        for trxdata in trxs:
            if trxdata[key] == pubkey and trxdata["TypeUrl"] == "quorum.pb.Person":
                rlt.append(trxdata)
        since = since or datetime.datetime.now()

        for trxdata in rlt:
            name = trxdata["Content"].get("name") or ""
            if self.trx.ts2datetime(trxdata) <= since:
                return name
        return name

    def ts2datetime(self, trxdata):
        # 把 rum 中的时间戳（纳米级）转换一下
        return datetime.datetime.fromtimestamp(
            int(int(trxdata["TimeStamp"]) / 1000000000)
        )

    def export(self, trxdata: Dict, trxs: List) -> Dict:
        """export data with refer_to data"""
        ts = self.trx.ts2datetime(trxdata)
        info = {
            "trx_id": trxdata["TrxId"],
            "trx_time": str(ts),
            "trx_type": self.trx_type(trxdata),
        }

        _content = trxdata["Content"]
        if "id" in _content:
            jid = _content["id"]
            info["refer_to"] = {
                "trx_id": jid,
                "text": self.get_trx_content(trxs, jid),
                "name": self.person_name(jid, trxs, ts),
            }
        elif "inreplyto" in _content:
            jid = _content["inreplyto"]["trxid"]
            info["refer_to"] = {
                "trx_id": jid,
                "text": self.get_trx_content(trxs, jid),
                "name": self.person_name(jid, trxs, ts),
            }

        if "content" in _content:
            info["text"] = _content["content"]
        if "image" in _content:
            if type(_content["image"]) == dict:
                info["imgs"] = [_content["image"]]
            else:
                info["imgs"] = _content["image"]
        return info

    def search_seeds(self, trxdata: Dict) -> List:
        """search seeds from trx data"""
        text = self.trx_text(trxdata).replace("\n", " ")

        if text == "":
            return []

        # 只能识别单个种子，但依然采用列表来处理结果
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

    def search_user(self, trxdata: Dict, xname):
        """
        搜寻昵称包含 xname 的用户，历史昵称也会搜索~
        返回 {pubkey:昵称} 作为结果
        """

        if trxdata["TypeUrl"] == "quorum.pb.Person":
            name = trxdata["Content"].get("name") or ""
            if name.lower().find(xname.lower()) >= 0:
                return {trxdata["Publisher"]: name}
        return {}
