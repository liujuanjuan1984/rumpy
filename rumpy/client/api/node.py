# -*- coding: utf-8 -*-
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI
from rumpy.client.api.group import RumGroup
import dataclasses


@dataclasses.dataclass
class CreateGroupParam:
    group_name: str
    consensus_type: str = "poa"
    encryption_type: str = "public"
    app_key: str = "group_timeline"

    def __post_init__(self):
        if self.consensus_type not in ["poa"]:  # ["poa","pos","pow"]:
            self.consensus_type = "poa"
        if self.encryption_type not in ["public"]:  # ["public","private"]:
            self.encryption_type = "public"
        if self.app_key not in ["group_timeline", "group_bbs", "group_note"]:
            self.app_key = "group_timeline"


@dataclasses.dataclass
class Block:
    BlockId: str
    GroupId: str
    ProducerPubKey: str
    Hash: str
    Signature: str
    TimeStamp: str


@dataclasses.dataclass
class Seed:
    genesis_block: Block.__dict__
    group_id: str
    group_name: str
    owner_pubkey: str
    owner_encryptpubkey: str
    consensus_type: str
    encryption_type: str
    cipher_key: str
    app_key: str
    signature: str


@dataclasses.dataclass
class NodeInfo:
    node_id: str
    node_publickey: str
    node_status: str
    node_type: str
    node_version: str
    peers: Dict


class RumNode(BaseRumAPI):
    @property
    def info(self):
        """return node info, dataclasses.dataclass type"""
        resp = self._get(f"{self.baseurl}/node")
        return NodeInfo(**resp)

    @property
    def id(self) -> str:
        """return node_id of this node"""
        return self.info.node_id

    @property
    def pubkey(self) -> str:
        """return pubkey of this node; be attention: node will get different pubkey in groups"""
        return self.info.node_publickey

    @property
    def status(self) -> str:
        """return status of this node;unkown,online or offline"""
        return self.info.node_status

    @property
    def type(self) -> str:
        """return type of this node;default peer"""
        return self.info.node_type

    @property
    def version(self) -> str:
        """return version of this node, refer to quorum version: https://github.com/rumsystem/quorum"""
        return self.info.node_version

    @property
    def peers(self) -> Dict:
        """return dict of different peers which this node has connected"""
        return self.info.peers

    @property
    def network(self) -> Dict:
        """return network info of this node"""
        return self._get(f"{self.baseurl}/network")

    def groups(self) -> List:
        """return list of group info which node has joined"""
        return self._get(f"{self.baseurl}/groups")["groups"]

    @property
    def groups_id(self) -> List:
        """return list of group_id which node has joined"""
        return [i["group_id"] for i in self.groups()]

    def group_info(self, group_id: str):
        """return a group info"""
        if self.is_joined(group_id):
            for ginfo in self.groups():
                if ginfo["group_id"] == group_id:
                    return ginfo
        return {"info": "you are not in this group."}

    def is_joined(self, group_id: str) -> bool:
        if group_id in self.groups_id:
            return True
        return False

    def create_group(self, group_name, **kargs):
        data = CreateGroupParam(group_name, **kargs).__dict__
        return self._post(f"{self.baseurl}/group", data)

    def is_seed(self, seed: Dict) -> bool:
        try:
            Seed(**seed)
            return True
        except Exception as e:
            print(e)
            return False

    def join_group(self, seed: Dict) -> Dict:
        """加入种子网络"""
        if self.is_seed(seed):
            return self._post(f"{self.baseurl}/group/join", seed)
        return {"error": "not a seed"}
