import logging
import urllib
from typing import Dict, List

from rumpy.api.base import BaseAPI
from rumpy.api.group import Group
from rumpy.types.data import *

logger = logging.getLogger(__name__)


class Node(BaseAPI):
    @property
    def info(self):
        """return node info, dataclasses.dataclass type"""
        resp = self._get("/node")
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
    def peers(self) -> Dict:
        """return dict of different peers which this node has connected"""
        return self.info.peers

    def connect(self, peers: List):
        """直连指定节点

        peers = [
            "/ip4/94.23.17.189/tcp/10666/p2p/16Uiu2HAmGTcDnhj3KVQUwVx8SGLyKBXQwfAxNayJdEwfsnUYKK4u"
            ]
        """
        return self._post("/network/peers", peers)

    def get_peers(self):
        """获取能 ping 通的节点"""
        return self._get("/network/peers/ping")

    def psping(self, peer_id: str):
        """ping 一个节点

        peer_id: 节点 ID, 例如 "16Uiu2HAxxxxxx...xxxxzEYBnEKFnao"
        """
        return self._post("/psping", {"peer_id": peer_id})

    @property
    def network(self) -> Dict:
        """return network info of this node"""
        return self._get("/network")

    @property
    def eth_addr(self):
        return self.network.get("eth_addr")

    def groups(self) -> List:
        """return list of group info which node has joined"""
        return self._get("/groups")["groups"]

    @property
    def groups_id(self) -> List:
        """return list of group_id which node has joined"""
        return [i["group_id"] for i in self.groups()]

    def backup(self):
        """Backup my group seed/keystore/config"""
        return self._get("/backup")

    def token(self):
        """Get a auth token for authorizing requests from remote"""
        return self._post("/token/apply", api_base=self._client.api_base_app)

    def token_refresh(self):
        """Get a new auth token"""
        return self._post("/token/refresh", api_base=self._client.api_base_app)

    def stats(self, start: str = None, end: str = None):
        """Get network stats summary

        param: start/end, str, query, "2022-04-28" or "2022-04-28 10:00" or "2022-04-28T10:00Z08:00"
        """
        api = "/network/stats"

        if start or end:
            query = "?"
            if start:
                query += f"&start={start}"
            if end:
                query += f"&end={end}"
            api += urllib.parse.quote(query, safe="?&/")

        return self._get(api)
