from typing import List, Dict, Any
from .base import BaseAPI
from .data import *


class Group(BaseAPI):
    def create(self, group_name: str, **kwargs) -> Dict:
        """create a group, return the seed of the group."""
        data = CreateGroupParam(group_name, **kwargs).__dict__
        return self._post(f"{self.baseurl}/group", data)

    def seed(self, group_id=None) -> Dict:
        """get the seed of a group which you've joined in."""
        group_id = group_id or self.group_id
        if self.is_joined(group_id):
            seed = self._get(f"{self.baseurl}/group/{group_id}/seed")
            if "error" not in seed:
                return seed

    def is_seed(self, seed: Dict) -> bool:
        try:
            Seed(**seed)
            return True
        except Exception as e:
            print(e)
            return False

    def info(self, group_id=None):
        """return group info,type: datacalss"""
        group_id = group_id or self.group_id
        for info in self.node.groups():
            if info["group_id"] == group_id:
                return GroupInfo(**info)

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        if not self.is_seed(seed):
            raise ValueError("not a seed or the seed could not be identified.")
        return self._post(f"{self.baseurl}/group/join", seed)

    def is_joined(self, group_id: str = None) -> bool:
        group_id = group_id or self.group_id
        if group_id in self.node.groups_id:
            return True
        return False

    def leave(self, group_id=None):
        """leave a group"""
        group_id = group_id or self.group_id
        if self.is_joined(group_id):
            return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})

    def clear(self, group_id=None):
        """clear data of a group"""
        group_id = group_id or self.group_id
        return self._post(f"{self.baseurl}/group/clear", {"group_id": group_id})

    def startsync(self, group_id=None):
        group_id = group_id or self.group_id
        if self.is_joined(group_id):
            return self._post(f"{self.baseurl}/group/{group_id}/startsync")

    def content(self, group_id=None) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        group_id = group_id or self.group_id
        if self.is_joined(group_id):
            return self._get(f"{self.baseurl}/group/{group_id}/content") or []

    def content_trxs(
        self,
        group_id=None,
        trx_id: str = None,
        num: int = 20,
        is_reverse=False,
        is_include_starttrx=False,
    ) -> List:
        """requests the content trxs of a group,return the list of the trxs data."""
        group_id = group_id or self.group_id
        if not self.is_joined(group_id):
            return []

        url = self.baseurl.replace("api", "app/api")

        if trx_id:
            apiurl = f"{url}/group/{group_id}/content?num={num}&starttrx={trx_id}&reverse={str(is_reverse).lower()}&includestarttrx={str(is_include_starttrx).lower()}"
        else:
            apiurl = f"{url}/group/{group_id}/content?num={num}&start=0"
        trxs = self._post(apiurl) or []
        return self.trxs_unique(trxs)

    def _send(self, group_id=None, obj: Dict = None, sendtype=None) -> Dict:
        """return the {trx_id:trx_id} of this action if send successed"""
        group_id = group_id or self.group_id
        if self.is_joined(group_id):
            p = {"type": sendtype, "object": obj, "target": group_id}
            data = ContentParams(**p).__dict__
            return self._post(f"{self.baseurl}/group/content", data)

    def like(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Like")

    def dislike(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Dislike")

    def send_note(self, group_id=None, **kwargs):
        """send note to a group. can be used to send: text only,image only,text with image,reply...etc"""
        group_id = group_id or self.group_id
        p = ContentObjParams(**kwargs)
        if p.content == None and p.image == None:
            raise ValueError("need some content. images,text,or both.")
        return self._send(group_id, obj=p.__dict__, sendtype="Add")

    def reply(self, content: str, trx_id: str):
        return self.send_note(content=content, inreplyto=trx_id)

    def send_text(self, content: str, name: str = None):
        """post text cotnent to group"""
        return self.send_note(content=content, name=name)

    def send_img(self, image):
        """post an image to group"""
        return self.send_note(image=[image])

    def block(self, group_id: str = None, block_id: str = None):
        """get the info of a block in a group"""
        group_id = group_id or self.group_id
        return self._get(f"{self.baseurl}/block/{group_id}/{block_id}")

    def is_owner(self, group_id: str = None) -> bool:
        """return True if I create this group else False"""
        ginfo = self.info(group_id or self.group_id)
        if isinstance(ginfo, GroupInfo) and ginfo.owner_pubkey == ginfo.user_pubkey:
            return True
        return False

    def trxs_by(self, pubkeys):
        trxs = self.content()
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        return trxs_by

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

    def trx(self, group_id: str = None, trx_id: str = None):
        group_id = group_id or self.group_id
        try:
            resp = self.content_trxs(
                group_id=group_id, trx_id=trx_id, num=1, is_include_starttrx=True
            )
            if len(resp) > 1:
                print("somthing is error", resp)
            elif len(resp) == 0:
                raise ValueError(f"nothing got. {resp} {trx_id} {group_id}")
            else:
                return resp[0]
        except Exception as e:
            print(e)
            return self._get(f"{self.baseurl}/trx/{group_id}/{trx_id}")
        return {"error": "nothing got."}

    def trxs_unique(self, trxs):
        """remove the duplicate trx from the trxs list"""
        new = {}
        for trx in trxs:
            if trx["TrxId"] not in new:
                new[trx["TrxId"]] = trx
        return [new[i] for i in new]
