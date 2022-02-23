import json
from typing import List, Dict, Any
from .base import BaseAPI
from .group import Group
from .data import *


class GroupConfig(BaseAPI):
    """config apis/methods for chainconfig, appconfig, user profile config.

    Args:
        BaseAPI (class): base class of rumpy api.
    """

    def _check_mode(self, mode: str):
        if mode.lower() not in ["dny", "deny", "allow", "alw"]:
            raise ValueError(f"{mode} mode must be one of ['deny','allow']")
        elif mode.lower() in ["dny", "deny"]:
            return "dny"
        elif mode.lower() in ["alw", "allow"]:
            return "alw"

    def _check_trx_type(self, trx_type: str):
        if trx_type.upper() not in TRX_TYPES:
            raise ValueError(f"{trx_type} must be one of {TRX_TYPES}")
        return trx_type.lower()

    def trx_auth_type(self, trx_type: str = "POST"):
        trx_type = self._check_trx_type(trx_type)
        return self._get(f"{self.baseurl}/group/{self.group_id}/trx/auth/{trx_type}")

    @property
    def auth_type(self):
        rlt = {}
        for i in TRX_TYPES:
            rlt.update(self.trx_auth_type(i))
        return rlt

    def set_trx_auth_type(
        self, trx_type: str, mode: str, memo: str = "set trx auth type"
    ):

        mode = self._check_mode(mode)
        trx_type = self._check_trx_type(trx_type)
        if not memo:
            raise ValueError("say something in param:memo")

        relay = {
            "group_id": self.group_id,
            "type": "set_trx_auth_mode",
            "config": json.dumps(
                {"trx_type": trx_type, "trx_auth_mode": f"follow_{mode}_list"}
            ),
            "Memo": memo,
        }
        return self._post(f"{self.baseurl}/group/chainconfig", relay)

    def _update_list(
        self, pubkey: str, mode: str, memo: str = "update list", trx_types: List = None
    ):

        mode = self._check_mode(mode)
        trx_types = trx_types or ["post"]
        for trx_type in trx_types:
            self._check_trx_type(trx_type)

        relay = {
            "group_id": self.group_id,
            "type": f"upd_{mode}_list",
            "config": json.dumps(
                {"action": "add", "pubkey": pubkey, "trx_type": trx_types}
            ),
            "Memo": memo,
        }
        return self._post(f"{self.baseurl}/group/chainconfig", relay)

    def update_allow_list(
        self, pubkey: str, memo: str = "update allow list", trx_types: List = None
    ):
        return self._update_list(pubkey, "alw", memo, trx_types)

    def update_deny_list(
        self, pubkey: str, memo: str = "update deny list", trx_types: List = None
    ):
        return self._update_list(pubkey, "dny", memo, trx_types)

    def _list(self, mode: str) -> List:
        if mode not in ["allow", "deny"]:
            raise ValueError("mode must be one of these: allow,deny")

        return self._get(f"{self.baseurl}/group/{self.group_id}/trx/{mode}list") or []

    @property
    def allow_list(self):
        return self._list("allow")

    @property
    def deny_list(self):
        return self._list("deny")

    def keylist(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/config/keylist")

    def keyname(self, keyname: str):
        return self._get(f"{self.baseurl}/group/{self.group_id}/config/{keyname}")

    def schema(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/schema")

    def announce(self, **kwargs):
        """annouce user or producer,add or remove"""
        p = AnnounceParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/announce", p)

    def announced_producers(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/announced/producers")

    def announced_users(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/announced/users")

    def producers(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/producers")

    def update_user(self, **kwargs):
        p = UserUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/user", p)

    def update_producer(self, **kwargs):
        p = ProducerUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/producer", p)

    """ #已废弃的接口
    def deniedlist(self):
        return self._get(f"{self.baseurl}/group/{self.group_id}/deniedlist")

    def update_deniedlist(self, **kwargs):
        p = DeniedlistUpdateParams(**kwargs).__dict__
        return self._post(f"{self.baseurl}/group/deniedlist", p)
    """
