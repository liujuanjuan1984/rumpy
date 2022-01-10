# -*- coding: utf-8 -*-
from typing import List, Dict
from rumpy.client.api.base import BaseRumAPI
from rumpy.client.api.group import RumGroup


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

    def create_group(
        self, group_name: str, consensus_type=None, encryption_type=None, app_key=None
    ) -> Dict:
        """创建种子网络"""
        if consensus_type not in ["poa"]:  # ["poa","pos","pow"]:
            consensus_type = "poa"
        if encryption_type not in ["public"]:  # ["public","private"]
            encryption_type = "public"
        if app_key not in ["group_timeline", "group_bbs", "group_note"]:
            app_key = "group_timeline"

        data = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }
        seed = self._post(f"{self.baseurl}/group", data)
        return seed

    def is_seed(self, seed: Dict) -> bool:
        # todo:seed检查
        return True

    def join_group(self, seed: Dict) -> Dict:
        """加入种子网络"""
        return self._post(f"{self.baseurl}/group/join", seed)
