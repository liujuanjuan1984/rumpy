# -*- coding: utf-8 -*-
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI
from rumpy.client.api.group import RumGroup
import dataclasses


class RumNode(BaseRumAPI):
    def info(self) -> Dict:
        return self._get(f"{self.baseurl}/node")

    @property
    def status(self) -> str:
        return self.info()["node_status"]

    @property
    def id(self) -> str:
        return self.info()["node_id"]

    @property
    def pubkey(self) -> str:
        return self.info()["node_publickey"]

    @property
    def version(self) -> str:
        return self.info()["node_version"]

    @property
    def network(self) -> Dict:
        return self._get(f"{self.baseurl}/network")

    def groups(self) -> List:
        return self._get(f"{self.baseurl}/groups")["groups"]

    @property
    def groups_id(self) -> List:
        """return list of group_id"""
        return [i["group_id"] for i in self.groups()]

    def is_joined(self, group_id: str) -> bool:
        if group_id in self.groups_id:
            return True
        return False

    def create_group(self, group_name, **kargs):
        data = CreateGroupParam(group_name, **kargs).__dict__
        return self._post(f"{self.baseurl}/group", data)

    def is_seed(self, seed: Dict) -> bool:
        # todo:seed检查
        return True

    def join_group(self, seed: Dict) -> Dict:
        """加入种子网络"""
        return self._post(f"{self.baseurl}/group/join", seed)


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
