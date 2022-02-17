import datetime
import pandas as pd
from typing import List, Dict, Any
from .base import BaseRumAPI
from .data import *


class RumGroup(BaseRumAPI):
    def create(self, group_name: str, **kwargs) -> Dict:
        """create a group, return the seed of the group."""
        return self.node.create_group(group_name, **kwargs)

    def seed(self, group_id: str) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.node.is_joined(group_id):
            return self._get(f"{self.baseurl}/group/{group_id}/seed")
        # raise ValueError(f"you are not in this group {group_id}.")

    def info(self, group_id: str):
        """return group info,type: datacalss"""
        info = self.node.group_info(group_id)
        return GroupInfo(**info)

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        return self.node.join_group(seed)

    def leave(self, group_id: str):
        """leave a group"""
        if self.node.is_joined(group_id):
            return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})
        # raise ValueError("you are not in this group.")

    def startsync(self, group_id: str):
        if self.node.is_joined(group_id):
            return self._post(f"{self.baseurl}/group/{group_id}/startsync")

    def trx(self, group_id: str, trx_id: str):
        try:
            resp = self.content_trxs(group_id, trx_id, num=1, is_include_starttrx=True)
            if len(resp) > 1:
                print("somthing is error", resp)
            return resp[0]
        except Exception as e:
            print(e)
            return self._get(f"{self.baseurl}/trx/{group_id}/{trx_id}")
        return {"error": "nothing got."}

    def content(self, group_id: str) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        return self._get(f"{self.baseurl}/group/{group_id}/content") or []

    def trxs_unique(self, trxs):
        """remove the duplicate trx from the trxs list"""
        new = {}
        for trx in trxs:
            if trx["TrxId"] not in new:
                new[trx["TrxId"]] = trx
        return [new[i] for i in new]

    def content_trxs(
        self,
        group_id: str,
        trx_id: str = None,
        num: int = 20,
        is_reverse=False,
        is_include_starttrx=False,
    ) -> List:
        """requests the content trxs of a group,return the list of the trxs data."""
        url = self.baseurl.replace("api", "app/api")

        if trx_id:
            apiurl = f"{url}/group/{group_id}/content?num={num}&starttrx={trx_id}&reverse={str(is_reverse).lower()}&includestarttrx={str(is_include_starttrx).lower()}"
        else:
            apiurl = f"{url}/group/{group_id}/content?num={num}&start=0"
            # raise ValueError(f"the trx {trx_id} isn't in this group {group_id}.")
        trxs = self._post(apiurl) or []

        return self.trxs_unique(trxs)

    def _send(self, group_id: str, obj: Dict, sendtype=None) -> Dict:
        """return the {trx_id:trx_id} of this action if send successed"""
        if self.node.is_joined(group_id):
            p = {"type": sendtype, "object": obj, "target": group_id}
            data = ContentParams(**p).__dict__
            return self._post(f"{self.baseurl}/group/content", data)
        # raise ValueError(f"you are not in this group {group_id}.")

    def like(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id, {"id": trx_id}, "Like")

    def dislike(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id, {"id": trx_id}, "Dislike")

    def send_note(self, group_id: str, **kwargs):
        """send note to a group. can be used to send: text only,image only,text with image,reply...etc"""
        p = ContentObjParams(**kwargs)
        if p.content == None and p.image == None:
            raise ValueError("need some content. images,text,or both.")
        return self._send(group_id, p.__dict__, "Add")

    def reply(self, group_id: str, content: str, trx_id: str):
        return self.send_note(group_id, content=content, inreplyto=trx_id)

    def send_text(self, group_id: str, content: str, name: str = None):
        """post text cotnent to group"""
        return self.send_note(group_id, content=content, name=name)

    def send_img(self, group_id: str, image):
        """post an image to group"""
        return self.send_note(group_id, image=[image])

    def block(self, group_id: str, block_id: str):
        """get the info of a block in a group"""
        return self._get(f"{self.baseurl}/block/{group_id}/{block_id}")

    def deniedlist(self, group_id: str):
        """get the deniedlist of a group"""
        return self._get(f"{self.baseurl}/group/{group_id}/deniedlist")

    def is_mygroup(self, group_id: str) -> bool:
        """return True if I create this group else False"""
        g = self.info(group_id)
        if g.owner_pubkey == g.user_pubkey:
            return True
        return False

    def trxs_by(self, group_id, pubkeys):
        trxs = self.content(group_id)
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        return trxs_by

    def announce(self, **kwargs):
        """annouce user or producer,add or remove"""
        p = AnnounceParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/announce", p)

    def announced_producers(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/announced/producers")

    def announced_users(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/announced/users")

    def producers(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/producers")

    def update_user(self, **kwargs):
        p = UserUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/user", p)

    def update_producer(self, **kwargs):
        p = ProducerUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/producer", p)

    def keylist(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/config/keylist")

    def keyname(self, group_id: str, keyname: str):
        return self._get(f"{self.baseurl}/group/{group_id}/config/{keyname}")

    def schema(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/schema")

    def update_deniedlist(self, **kwargs):
        p = DeniedlistUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/deniedlist", p)

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
