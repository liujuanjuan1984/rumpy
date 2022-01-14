# -*- coding: utf-8 -*-

import datetime
from typing import List, Dict, Any
from rumpy.client.api.base import BaseRumAPI
from rumpy.img import Img
import dataclasses


@dataclasses.dataclass
class ContentObjParams:
    """
    content: str,text
    name:str, title for group_bbs if need
    image: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs
    inreplyto:str,trx_id
    type: `Note`
    """

    content: str = None
    name: str = None
    image: List = None
    inreplyto: Any = None
    type: str = "Note"

    def __post_init__(self):
        if self.image != None:
            ximgs = []
            for img in self.image:
                ximgs.append(Img().encode(img))
            self.image = ximgs

        if self.inreplyto != None:
            self.inreplyto = {"trxid": self.inreplyto}


@dataclasses.dataclass
class ContentParams:
    type: Any
    object: Dict
    target: str  # group_id

    def __post_init__(self):
        if self.type not in [4, "Add", "Like", "Dislike"]:
            self.type = "Add"
        self.target = {"id": self.target, "type": "Group"}


@dataclasses.dataclass
class GroupInfo:
    group_id: str
    group_name: str
    owner_pubkey: str
    user_pubkey: str
    consensus_type: str
    encryption_type: str
    cipher_key: str
    app_key: str
    last_updated: int
    highest_height: int  # 区块数
    highest_block_id: str
    group_status: str


@dataclasses.dataclass
class DeniedlistUpdateParams:
    peer_id: str  # node_id ???QmQZcijmay86LFCDFiuD8ToNhZwCYZ9XaNpeDWVWWJY222
    group_id: str
    action: str  # "del" or add


@dataclasses.dataclass
class ProducerAnnounceParams:
    group_id: str
    action: str = "add"
    type: str = "producer"
    memo: str = "producer, realiable and cheap, online 24hr"


@dataclasses.dataclass
class ProducerUpdateParams:
    producer_pubkey: str
    group_id: str
    action: str  # "add" or "remove"


class RumGroup(BaseRumAPI):
    def create(self, group_name: str, **kargs) -> Dict:
        """create a group, return the seed of the group."""
        return self.node.create_group(group_name, **kargs)

    def seed(self, group_id: str) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.node.is_joined(group_id):
            return self._get(f"{self.baseurl}/group/{group_id}/seed")
        return {"error": "you are not in this group."}

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        return self.node.join_group(seed)

    def leave(self, group_id: str):
        """leave a group"""
        if self.node.is_joined(group_id):
            return self._post(f"{self.baseurl}/group/leave", {"group_id": group_id})
        return {"info": "you are not in this group."}

    def content(self, group_id: str) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        return self._get(f"{self.baseurl}/group/{group_id}/content") or []

    def _send(self, group_id: str, obj: Dict, sendtype=None) -> Dict:
        """return the {trx_id:trx_id} of this action if send successed"""
        if not self.node.is_joined(group_id):
            return {"error": "you are not in this group."}
        p = {"type": sendtype, "object": obj, "target": group_id}
        data = ContentParams(**p).__dict__
        return self._post(f"{self.baseurl}/group/content", data)

    def like(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id, {"id": trx_id}, "Like")

    def dislike(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id, {"id": trx_id}, "Dislike")

    def send_note(self, group_id: str, **kwargs):
        """send note to a group. can be used to send: text only,image only,text with image,reply...etc"""
        p = ContentObjParams(**kwargs)
        if p.content == None and p.image == None:
            return {"error": "need some content. images,text,or both."}
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

    def info(self, group_id: str):
        """return group info,type: datacalss"""
        info = self.node.group_info(group_id)
        return GroupInfo(**info)

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

    def content_by(self, group_id, pubkeys):
        trxs = self.content(group_id)
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        content_by = [self.trx.export(i, trxs) for i in trxs_by]
        return content_by

    def announced_producers(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/announced/producers")

    def producers(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/producers")

    def announced_users(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/announced/users")

    def keylist(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/config/keylist")

    def keyname(self, group_id: str, keyname: str):
        return self._get(f"{self.baseurl}/group/{group_id}/config/{keyname}")

    def schema(self, group_id: str):
        return self._get(f"{self.baseurl}/group/{group_id}/schema")

    def update_deniedlist(self, **kwargs):
        p = DeniedlistUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/deniedlist", p)

    def announce_producer(self, **kwargs):
        p = ProducerAnnounceParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/announce", p)

    def update_producer(self, **kwargs):
        p = ProducerUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/producer", p)

    def search_seeds(self, group_id: str) -> Dict:
        """search seeds from group"""
        rlt = {}
        for trxdata in self.content(group_id):
            iseeds = self.trx.search_seeds(trxdata)
            for iseed in iseeds:
                if iseed["group_id"] not in rlt:
                    rlt[iseed["group_id"]] = iseed
        if group_id not in rlt:
            rlt[group_id] = self.seed(group_id)
        return rlt
