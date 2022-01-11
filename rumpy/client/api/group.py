# -*- coding: utf-8 -*-

import base64
import datetime
import uuid
import os
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI


class RumGroup(BaseRumAPI):
    def create(
        self, group_name: str, consensus_type=None, encryption_type=None, app_key=None
    ):
        return self.node.create_group(
            group_name, consensus_type, encryption_type, app_key
        )

    def join(self, seed: Dict):
        return self.node.join_group(seed)

    def seed(self, group_id: str):  # todo：需要依赖 quorum 新版本
        """获取种子网络的种子"""
        return self._get(f"{self.baseurl}/group/{group_id}/seed")

    def content(self, group_id: str):
        """获取种子网络的内容（返回由 trx 构成的列表）"""
        return self._get(f"{self.baseurl}/group/{group_id}/content")

    def _send(self, data):
        return self._post(f"{self.baseurl}/group/content", data)

    def like(self, group_id: str, trx_id: str, is_like=True):
        """喜欢一条内容"""
        if is_like:
            is_like = "Like"
        else:
            is_like = "Dislike"
        data = {
            "type": is_like,
            "object": {"id": trx_id},
            "target": {"id": group_id, "type": "Group"},
        }
        return self._send(data)

    def dislike(self, group_id: str, trx_id: str):
        return self.like(group_id, trx_id, False)

    def _image(self, imgpath: str):
        with open(imgpath, "rb") as f:
            imgbytes = f.read()

        return {
            "mediaType": imgpath.split(".")[-1],
            "content": base64.b64encode(imgbytes).decode("utf-8"),
            "name": f"{uuid.uuid4()}-{datetime.datetime.now().isoformat()}",
        }

    def send_note(self, group_id: str, text=None, imgs=None, trx_id=None):
        if not (text or imgs):
            return print(datetime.datetime.now(), "图片、文本都为空")

        obj = {"type": "Note"}
        if text:
            obj["content"] = text
        if imgs:
            for img in imgs:
                if type(img) == str:
                    img = self._image(img)
                if type(img) == dict:
                    if "image" not in obj:
                        obj["image"] = []
                    obj["image"].append(img)
        if trx_id:
            obj["inreplyto"] = {"trxid": trx_id}

        # todo:检查trx_id是否在当前group

        data = {
            "type": "Add",
            "object": obj,
            "target": {"id": group_id, "type": "Group"},
        }
        return self._send(data)

    def block(self, group_id: str, block_id: str):
        return self._get(f"{self.baseurl}/block/{group_id}/{block_id}")

    def deniedlist(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/deniedlist")

    def leave(self, group_id: str):  # todo:seed检查
        """leave gropu"""
        return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})
