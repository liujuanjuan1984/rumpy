from typing import List, Dict
from rumpy.client.api.base import BaseAPI
from rumpy.client.api.group import Group
from rumpy.client.api.data import *


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
        """return status of this node; unknown, online or offline"""
        return self.info.node_status

    @property
    def type(self) -> str:
        """return type of this node; default peer"""
        return self.info.node_type

    @property
    def version(self) -> str:
        """return version of this node, refer to quorum version: https://github.com/rumsystem/quorum"""
        return self.info.node_version

    @property
    def peers(self) -> Dict:
        """return dict of different peers which this node has connected"""
        return self.info.peers

    def connect(self, peers: List):
        """直连指定节点

        peers = [
            "/ip4/94.23.17.189/tcp/10666/p2p/16Uiu2HAmGTcDnhj3KVQUwVx8SGLyKBXQwfAxNayJdEwfsnUYKK4u"
            ]
        """
        return self._post(f"{self.baseurl}/network/peers", peers)

    def get_peers(self):
        """获取能 ping 通的节点"""
        return self._get(f"{self.baseurl}/network/peers/ping")

    def psping(self, peer_id: str):
        """ping 一个节点

        peer_id: 节点 ID, 例如 "16Uiu2HAxxxxxx...xxxxzEYBnEKFnao"
        """
        return self._post(f"{self.baseurl}/psping", {"peer_id": peer_id})

    @property
    def network(self) -> Dict:
        """return network info of this node"""
        return self._get(f"{self.baseurl}/network")

    @property
    def eth_addr(self):
        return self.network.get("eth_addr")

    def groups(self) -> List:
        """return list of group info which node has joined"""
        return self._get(f"{self.baseurl}/groups")["groups"]

    @property
    def groups_id(self) -> List:
        """return list of group_id which node has joined"""
        return [i["group_id"] for i in self.groups()]

    def backup(self):
        """Backup my group seed/keystore/config"""
        return self._get(f"{self.baseurl}/backup")

    def token(self):
        """Get a auth token for authorizing requests from remote"""
        return self._post(f"{self.baseurl_app}/token/apply")

    def token_refresh(self):
        """Get a new auth token"""
        return self._post(f"{self.baseurl_app}/token/refresh")

    def stats(self):
        """Get network stats summary"""
        return self._post(f"{self.baseurl_app}/network/stats")
