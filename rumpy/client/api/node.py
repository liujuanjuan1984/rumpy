from typing import List, Dict
from .base import BaseAPI
from .group import Group
from .data import *


class Node(BaseAPI):
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

    def group_info(self, group_id: str = None):
        """return a group info"""
        group_id = group_id or self.group_id
        if not self.is_joined(group_id):
            raise ValueError(f"you are not in this group {group_id}.")
        for ginfo in self.groups():
            if ginfo["group_id"] == group_id:
                return ginfo

    def is_joined(self, group_id: str = None) -> bool:
        group_id = group_id or self.group_id
        if group_id in self.groups_id:
            return True
        return False
