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
    ) -> Dict:
        """
        create a group, return the seed of the group.

        kwargs = {
            "group_name":"test_rumpy",
            "consensus_type":"poa",
            "encryption_type":"public",
            "app_key":"group_timeline",
        }

        """
        return self.node.create_group(
            group_name, consensus_type, encryption_type, app_key
        )

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        return self.node.join_group(seed)

    def seed(self, group_id: str) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.node.is_joined(group_id):
            return self._get(f"{self.baseurl}/group/{group_id}/seed")
        return {}

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

    def _image(self, imgpath: str):
        """init a image object from imgpath(the path of a image)"""
        with open(imgpath, "rb") as f:
            imgbytes = f.read()

        return {
            "mediaType": imgpath.split(".")[-1],
            "content": base64.b64encode(imgbytes).decode("utf-8"),
            "name": f"{uuid.uuid4()}-{datetime.datetime.now().isoformat()}",
        }

    def send_note(self, group_id: str, text=None, imgs=None, trx_id=None):
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
        """get the info of a block in a group"""
        return self._get(f"{self.baseurl}/block/{group_id}/{block_id}")

    def deniedlist(self, group_id: str):
        """get the deniedlist of a group"""
        return self._get(f"{self.baseurl}/group/{group_id}/deniedlist")

    def leave(self, group_id: str):
        """leave a group"""
        return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})
