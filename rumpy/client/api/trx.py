# -*- coding: utf-8 -*-

import time
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI


class RumTrx(BaseRumAPI):
    def info(self, group_id: str, trx_id: str):
        return self._get(f"{self.baseurl}/trx/{group_id}/{trx_id}")

    def _timestamp(self, timestamp):
        """把 rum 中的时间戳（纳米级）转换为年月日时分秒的字符串"""
        timeArray = time.localtime(int(timestamp / 1000000000))
        strtime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return strtime

    def timestamp(self, trxdata: Dict):
        return self._timestamp(trxdata["TimeStamp"])

    def trx_type(self, trxdata: Dict):
        """get type of trx, trx is one of group content list"""
        if trxdata["TypeUrl"] == "quorum.pb.Person":
            return "person"
        content = trxdata["Content"]
        if "type" not in content:
            return "other"
        trxtype = content["type"]
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
        return trxtype.lower()  # "like","dislike"

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

    def person_name(self, trx_id, trxs, since=None):
        """get the lastest name of the person published the trx_id"""
        trxdata = self.trxdata(trx_id, trxs)
        pubkey = trxdata["Publisher"]
        rlt = []
        for trxdata in trxs:
            if (
                trxdata["Publisher"] == pubkey
                and trxdata["TypeUrl"] == "quorum.pb.Person"
            ):
                rlt.append(trxdata)
        if since == None:
            since = str(datetime.datetime.now())[:19]
        for trxdata in rlt:
            if "name" in trxdata["Content"]:
                if self.timestamp(trxdata) <= since:
                    return trxdata["Content"]["name"]
        return ""

    def export(self, trxdata: Dict, trxs: List) -> Dict:
        """export data with refer_to data"""
        ts = self.timestamp(trxdata)
        info = {
            "trx_id": trxdata["TrxId"],
            "trx_time": ts,
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
