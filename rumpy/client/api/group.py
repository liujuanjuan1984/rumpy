# -*- coding: utf-8 -*-

import datetime
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI
from rumpy.img import Img


class RumGroup(BaseRumAPI):
    def create(self, group_name: str, **kargs) -> Dict:
        """create a group, return the seed of the group."""
        return self.node.create_group(group_name, **kargs)

    def seed(self, group_id: str) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.node.is_joined(group_id):
            return self._get(f"{self.baseurl}/group/{group_id}/seed")
        return {}

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        return self.node.join_group(seed)

    def leave(self, group_id: str):
        """leave a group"""
        return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})

    def content(self, group_id: str) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        return self._get(f"{self.baseurl}/group/{group_id}/content") or []

    def _send(self, data: Dict) -> Dict:
        """return the {"trx_id":"xxx"}"""
        return self._post(f"{self.baseurl}/group/content", data)

    def like(self, group_id: str, trx_id: str, is_like=True) -> Dict:
        """like a object(e.g.content/reply,any trx)"""
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

    def dislike(self, group_id: str, trx_id: str) -> Dict:
        """dislike"""
        return self.like(group_id, trx_id, False)

    def send_note(
        self, group_id: str, text: str = None, imgs: list = None, trx_id: str = None
    ):
        """send note to a group. can be used to send: text only,image only,text with image,reply...etc"""
        if not (text or imgs):
            error = {
                "error": "imgs and text are both None. should: imgs or text or both."
            }
            return error

        obj = {"type": "Note"}
        if text:
            obj["content"] = text
        if imgs:
            for img in imgs:
                if "image" not in obj:
                    obj["image"] = []
                obj["image"].append(Img().encode(img))
        if trx_id:
            obj["inreplyto"] = {"trxid": trx_id}

        # todo:检查trx_id是否在当前group

        data = {
            "type": "Add",
            "object": obj,
            "target": {"id": group_id, "type": "Group"},
        }
        return self._send(data)

    def reply(self, group_id: str, text, trx_id):
        return self.send_note(group_id, text, None, trx_id)

    def send_txt(self, group_id, text):
        return self.send_note(group_id, text)

    def send_img(self, group_id, image):
        return self.send_note(group_id, None, [image], None)

    def block(self, group_id: str, block_id: str):
        """get the info of a block in a group"""
        return self._get(f"{self.baseurl}/block/{group_id}/{block_id}")

    def deniedlist(self, group_id: str):
        """get the deniedlist of a group"""
        return self._get(f"{self.baseurl}/group/{group_id}/deniedlist")
