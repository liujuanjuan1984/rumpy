import datetime
from typing import List, Dict
import json
from rumpy import RumClient
from rumpy import JsonFile


class WhoSays(RumClient):
    """Rum 产品想法：筛选某人所说，并转发到指定组"""

    def do(
        self,
        filepath: str,
        name: str,
        names_info: Dict[str, List],
        toshare_group_id: str,
    ):
        """
        filepath: 数据存储文件 .json
        name：这个人的昵称/名字，构建转发文本某某说
        names_info：这个人在多个group的多个 pubkey，用来标记who是他
        toshare_group_id：转发到指定的那个组
        """

        data = JsonFile(filepath).read({})  # 读取本地已有数据
        for group_id in names_info:
            pubkeys = names_info[group_id]
            trxs = self.group.content(group_id)  # 获取链上数据 group chain
            data = self._search(pubkeys, group_id, data, trxs)
            JsonFile(filepath).write(data)
            data = self._send(name, toshare_group_id, data, trxs)
            JsonFile(filepath).write(data)

    def _search(self, pubkeys: List, group_id: str, data: Dict, trxs: List) -> Dict:

        for trxdata in trxs:
            if trxdata["Publisher"] not in pubkeys:  # 不是此人发的
                continue
            if trxdata["TrxId"] in data:  # 已经被抓取过了
                continue
            data[trxdata["TrxId"]] = {
                "seed": self.group.seed(group_id),
                "trx": trxdata,
                "created_at": str(datetime.datetime.now()),
            }
        return data

    def _send(self, name: str, toshare_group_id: str, data: Dict, trxs: List) -> Dict:
        """发布内容并更新发布状态"""
        for trx_id in data:
            if "shared" not in data[trx_id]:
                data[trx_id]["shared"] = []
            if toshare_group_id in data[trx_id]["shared"]:
                continue
            obj = self._obj(data[trx_id]["trx"], trxs)
            obj["text"] = f"{name} {obj['text']}\n\n来源: " + json.dumps(
                data[trx_id]["seed"]
            )

            if self.group.send_note(toshare_group_id, **obj):
                data[trx_id]["shared"].append(toshare_group_id)
        return data

    def _obj(self, trxdata: Dict, trxs: List) -> Dict:

        ts = self.trx.timestamp(trxdata)
        trxtype = self.trx.trx_type(trxdata)

        # 点赞/踩
        _info = {"like": "赞", "dislike": "踩"}
        if trxtype in _info:
            jid = trxdata["Content"]["id"]
            jnote = self.trx.get_trx_content(trxs, jid)
            text = f"{ts} 点{_info[trxtype]}给：\n{jnote}"
            return {"text": text}

        # 个人信息
        if trxtype in ["person"]:
            return {"text": f"{ts} 更新了个人信息。"}

        if trxtype in ["announce"]:
            return {"text": f"{ts} 处理了通知请求。"}

        obj = {}
        _content = trxdata["Content"]
        if "content" in _content:
            obj["text"] = f"{ts} 说：\n" + _content["content"]
        if "image" in _content:
            obj["imgs"] = _content["image"]
            if "content" not in _content:
                obj["text"] = f"{ts} 发布了图片："

        if "text" not in obj:
            obj["text"] = f"{ts} 冒了个泡。"

        # 回复
        if trxtype == "reply":
            jid = _content["inreplyto"]["trxid"]
            jnote = self.trx.get_trx_content(trxs, jid)
            obj["text"] += f"\n\n回复给：\n{jnote}"

        return obj

        if trxtype in ["text_only", "image_text"]:
            inote = trxdata["Content"]["content"]
            text = f"{name} {ts} 说：\n{inote}"

        elif trxtype == "person":
            text = f"{name} {ts} 修改了个人信息"
        else:
            text = ""
        return text
