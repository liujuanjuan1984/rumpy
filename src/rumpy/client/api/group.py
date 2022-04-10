from typing import List, Dict, Any
from rumpy.client.api.base import BaseAPI
from rumpy.client.api.data import *


class Group(BaseAPI):
    def create(
        self,
        group_name: str,
        app_key: str = "group_timeline",
        consensus_type="poa",
        encryption_type="public",
    ) -> Dict:
        """create a group, return the seed of the group.
        app_key: 可以为自定义字段，只是如果不是 group_timeline,group_post,group_note 这三种，可能无法在 rumapp 中识别，如果是自己开发客户端，则可以自定义类型
        """

        if encryption_type.lower() not in ["public", "private"]:
            raise ValueError("encryption_type should be `public` or `private`")

        relay = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }

        return self._post(f"{self.baseurl}/group", relay)

    def seed(self) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.is_joined():
            seed = self._get(f"{self.baseurl}/group/{self.group_id}/seed")
            if "error" not in seed:
                return seed

    def is_seed(self, seed: Dict) -> bool:
        try:
            Seed(**seed)
            return True
        except Exception as e:
            print(e)
            return False

    def info(self):
        """return group info,type: datacalss"""
        if self.is_joined():
            for info in self.node.groups():
                if info["group_id"] == self.group_id:
                    return GroupInfo(**info)
        else:
            raise ValueError(f"you are not in this group.{self.group_id}")

    @property
    def pubkey(self):
        return self.info().user_pubkey

    @property
    def owner(self):
        return self.info().owner_pubkey

    @property
    def eth_addr(self):
        return self.info().user_eth_addr

    @property
    def type(self):
        self._check_group_id()
        return self.seed().get("app_key")

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        if not self.is_seed(seed):
            raise ValueError("not a seed or the seed could not be identified.")
        return self._post(f"{self.baseurl}/group/join", seed)

    def is_joined(self) -> bool:
        self._check_group_id()
        if self.group_id in self.node.groups_id:
            return True
        return False

    def leave(self):
        """leave a group"""
        if self.is_joined():
            return self._post(
                f"{self.baseurl}/group/leave", {"group_id": self.group_id}
            )

    def clear(self):
        """clear data of a group"""
        self._check_group_id()
        return self._post(f"{self.baseurl}/group/clear", {"group_id": self.group_id})

    def startsync(self):
        if self.is_joined():
            return self._post(f"{self.baseurl}/group/{self.group_id}/startsync")

    def content(self) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        if self.is_joined():
            return self._get(f"{self.baseurl}/group/{self.group_id}/content") or []

    def content_trxs(
        self,
        trx_id: str = None,
        num: int = 20,
        is_reverse=False,
        is_include_starttrx=False,
    ) -> List:
        """requests the content trxs of a group,return the list of the trxs data."""

        if not self.is_joined():
            return []

        url = self.baseurl.replace("api", "app/api")

        if trx_id:
            apiurl = f"{url}/group/{self.group_id}/content?num={num}&starttrx={trx_id}&reverse={str(is_reverse).lower()}&includestarttrx={str(is_include_starttrx).lower()}"
        else:
            apiurl = f"{url}/group/{self.group_id}/content?num={num}&start=0"
        trxs = self._post(apiurl) or []
        return self.trxs_unique(trxs)

    def _send(self, obj: Dict = None, sendtype="Add") -> Dict:
        """return the {trx_id:trx_id} of this action if send successed"""

        self._check_group_id()
        if sendtype not in [4, "Add", "Like", "Dislike"]:
            sendtype = "Add"

        relay = {
            "type": sendtype,
            "object": obj,
            "target": {"id": self.group_id, "type": "Group"},
        }

        return self._post(f"{self.baseurl}/group/content", relay)

    def like(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Like")

    def dislike(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Dislike")

    def send_note(
        self, content=None, name: str = None, image: List = None, inreplyto: str = None
    ):
        """send note to a group. can be used to send: text only,image only,text with image,reply...etc
        content: str,text
        name:str, title for group_post if needed
        image: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs
        """
        obj = {"type": "Note"}

        if content:
            obj["content"] = content
        if name:
            obj["name"] = name
        if image:
            obj["image"] = [ImgObj(img).__dict__ for img in image]
        if inreplyto:
            obj["inreplyto"] = {"trxid": inreplyto}

        if obj.get("content") == None and obj.get("image") == None:
            raise ValueError("need some content. images,text,or both.")

        return self._send(obj=obj)

    def reply(self, content: str, trx_id: str):
        return self.send_note(content=content, inreplyto=trx_id)

    def send_text(self, content: str, name: str = None):
        """post text cotnent to group"""
        return self.send_note(content=content, name=name)

    def send_img(self, image):
        """post an image to group"""
        return self.send_note(image=[image])

    def block(self, block_id: str = None):
        """get the info of a block in a group"""
        self._check_group_id()
        return self._get(f"{self.baseurl}/block/{self.group_id}/{block_id}")

    def is_owner(self) -> bool:
        """return True if I create this group else False"""
        ginfo = self.info()
        if isinstance(ginfo, GroupInfo) and ginfo.owner_pubkey == ginfo.user_pubkey:
            return True
        return False

    def all_content_trxs(self, trx_id=None):
        """get all the trxs of content started from trx_id"""
        trxs = []
        checked_trxids = []
        while True:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            newtrxs = self.content_trxs(trx_id=trx_id, num=100)
            if len(newtrxs) == 0:
                break
            trxs.extend(newtrxs)
            trx_id = self.last_trx_id(trx_id, newtrxs)
        return trxs

    def last_trx_id(self, trx_id, trxs):
        """get the last-trx_id of trxs which if different from given trx_id"""
        for i in range(-1, -1 * len(trxs), -1):
            tid = trxs[i]["TrxId"]
            if tid != trx_id:
                return tid
        return trx_id

    def trxs_by(self, pubkeys, trx_id=None):
        trxs = self.all_content_trxs(trx_id)
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        return trxs_by

    def trx_type(self, trxdata: Dict):
        """get type of trx, trx is one of group content list"""
        if "TypeUrl" not in trxdata:
            return "encrypted"
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

    def trx(self, trx_id: str = None):
        try:
            resp = self.content_trxs(trx_id=trx_id, num=1, is_include_starttrx=True)
            if len(resp) > 1:
                print("somthing is error", resp)
            elif len(resp) == 0:
                raise ValueError(f"nothing got. {resp} {trx_id} {self.group_id}")
            else:
                return resp[0]
        except Exception as e:
            print(e)
            return self._get(f"{self.baseurl}/trx/{self.group_id}/{trx_id}")
        return {"error": "nothing got."}

    def trxs_unique(self, trxs):
        """remove the duplicate trx from the trxs list"""
        new = {}
        for trx in trxs:
            if trx["TrxId"] not in new:
                new[trx["TrxId"]] = trx
        return [new[i] for i in new]

    def pubqueue(self):
        self._check_group_id()
        resp = self._get(f"{self.baseurl}/group/{self.group_id}/pubqueue")
        return resp.get("Data")
