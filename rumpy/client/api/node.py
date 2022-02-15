# -*- coding: utf-8 -*-

import json
from typing import List, Dict
from dataclasses import dataclass
from .base import BaseRumAPI
from .group import RumGroup
from ..data import CreateGroupParam, Seed


@dataclass
class NodeInfo:
    node_id: str
    node_publickey: str
    node_status: str
    node_type: str
    node_version: str
    peers: Dict

    def values(self):
        """供 sql 调用"""
        return (
            self.node_id,
            self.node_publickey,
            self.node_status,
            self.node_type,
            self.node_version,
            json.dumps(self.peers),
        )


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
        if not self.is_joined(group_id):
            raise ValueError(f"you are not in this group {group_id}.")
        for ginfo in self.groups():
            if ginfo["group_id"] == group_id:
                return ginfo

    def is_joined(self, group_id: str) -> bool:
        if group_id in self.groups_id:
            return True
        return False

    def create_group(self, group_name, **kwargs):
        data = CreateGroupParam(group_name, **kwargs).__dict__
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
        if not self.is_seed(seed):
            raise ValueError("not a seed or the seed could not be identified.")
        return self._post(f"{self.baseurl}/group/join", seed)

    def search_seeds(self) -> Dict:
        rlt = {}
        for group_id in self.groups_id:
            rlt.update(self.group.search_seeds(group_id))
        return rlt

    def search_user(self, xname):
        """
        搜寻昵称包含 xanme 的用户，历史记录也会搜寻到
        返回{group_id : {pubkey:[昵称]}
        """
        if not xname:
            raise ValueError("need piece of nickename to search.")
        rlt = {}
        for group_id in self.groups_id:
            irlt = self.group.search_user(group_id, xname)
            if len(irlt) > 0:
                rlt[group_id] = irlt
        return rlt
