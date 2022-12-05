import base64
import datetime
import json
import logging
import os
import time
import urllib
from typing import Any, Dict, List, Union

import filetype

import rumpy.utils as utils
from rumpy.api.base import BaseAPI
from rumpy.exceptions import *
from rumpy.types.data import *

logger = logging.getLogger(__name__)


class FullNodeAPI(BaseAPI):
    def node_info(self):
        """get node info"""
        return self._get("/api/v1/node")

    def _groups(self) -> List:
        """return list of groups info which this node has joined"""
        return self._get("/api/v1/groups")

    def group_info(self, group_id=None) -> Dict:
        """get the group info"""
        group_id = self.check_group_joined_as_required(group_id)
        info = {}
        for _info in self.groups():
            if _info["group_id"] == group_id:
                info = _info
                break
        return info

    def create_group(
        self,
        group_name: str,
        app_key: str = "group_timeline",
        consensus_type: str = "poa",
        encryption_type: str = "public",
    ) -> Dict:
        """create a group, return the seed of the group.

        group_name: 组名, 自定义, 不可更改
        consensus_type: 共识类型, "poa", "pos", "pow", 当前仅支持 "poa"
        encryption_type: 加密类型, "public" 公开, "private" 私有
        app_key: 可以为自定义字段，只是如果不是 group_timeline,
            group_post, group_note 这三种，可能无法在 rum-app 中识别，
            如果是自己开发客户端，则可以自定义类型

        创建成功, 返回值是一个种子, 通过它其他人可加入该组
        """
        # check encryption_type
        if encryption_type.lower() not in ("public", "private"):
            raise ParamValueError("encryption_type should be `public` or `private`")

        # check consensus_type
        if consensus_type.lower() not in ("poa",):
            raise ParamValueError(
                "consensus_type should be `poa` or `pos` or `pow`, but only `poa` is supported now.",
            )

        payload = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }

        return self._post("/api/v1/group", payload)

    def seed(self, group_id=None) -> str:
        """get the seed of a group which you've joined in."""
        group_id = self.check_group_joined_as_required(group_id)
        seed = self._get(f"/api/v1/group/{group_id}/seed")
        return seed.get("seed")

    def join_group(self, seed: str):
        """join a group with the seed of the group
        the seed is string startswith rum://
        """
        resp = self._post(f"/api/v2/group/join", {"seed": seed})
        return resp

    def leave_group(self, group_id=None):
        """leave a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post("/api/v1/group/leave", {"group_id": group_id})

    def clear_group(self, group_id=None):
        """clear data of a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post("/api/v1/group/clear", {"group_id": group_id})

    def block(self, block_id, group_id=None):
        """get the info of a block in a group, the block_id is uuid in old version, but int in new version"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/block/{group_id}/{block_id}")

    ################ utils apis ################

    def token_create(
        self, name: str, role: str, allow_groups: List, expires_at: int
    ):  # TODO: to fix expires_at
        """Create a new auth token, only allow access from localhost"""
        payload = {
            "name": name,
            "role": role,
            "allow_groups": allow_groups,
            "expires_at": expires_at,
        }
        return self._post("/app/api/v1/token/create", payload)

    def token_refresh(self):  # TODO: to fix
        """Get a new auth token"""
        return self._post("/app/api/v1/token/refresh")

    def pubkey_to_address(self, pubkey):
        """convert pubkey to address"""
        payload = {"encoded_pubkey": pubkey}
        resp = self._post("/api/v1/tools/pubkeytoaddr", payload)
        if addr := resp.get("addr"):
            return addr
        else:
            raise ParamValueError(f"pubkey_to_addr failed. pubkey:{pubkey},resp: {resp}")

    ################ network apis ################

    def network(self) -> Dict:
        """get network info of node"""
        return self._get("/api/v1/network")

    def connect_peers(self, peers: List):
        """connect to peers.
        one peer in the list is like:
        "/ip4/10x.xx.xxx.xxx/tcp/31124/p2p/16Uiu2H...uisLB"
        """
        return self._post("/api/v1/network/peers", peers)

    def ping_peers(self):
        """list all the peers which you've connected"""
        return self._get("/api/v1/network/peers/ping")

    def ping_peer(self, peer_id: str):
        """ping a peer with peer_id such as:
        "16Uiu2HAxxxxxx...xxxxzEYBnEKFnao"
        """
        return self._post("/api/v1/psping", {"peer_id": peer_id})

    def ask_for_relay(self, peers: List):
        """node in private network ask for relay servers
        one peer in the list is like:
        "/ip4/10x.xx.xxx.xxx/tcp/31124/p2p/16Uiu2H...uisLB"
        """
        return self._post("/api/v1/network/relay", peers)

    def network_stats(self, start: str = None, end: str = None):
        """旧API，目前无效。Get network stats summary
        param: start/end, str, query, "2022-04-28" or "2022-04-28 10:00" or "2022-04-28T10:00Z08:00"
        """
        api = utils.get_url(None, "/api/v1/network/stats", is_quote=True, start=start, end=end)
        return self._get(api)

    def startsync(self, group_id=None):
        """start sync data of a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post(f"/api/v1/group/{group_id}/startsync")

    ################ pubque apis ################

    def pubqueue(self, group_id=None) -> List:
        """get the pub queue list"""
        group_id = self.check_group_id_as_required(group_id)
        resp = self._get(f"/api/v1/group/{group_id}/pubqueue")
        return resp.get("Data")

    def ack(self, trx_ids: List):
        """ack the trxs"""
        if trx_ids == []:
            return True
        return self._post("/api/v1/trx/ack", {"trx_ids": trx_ids})

    def autoack(self, group_id=None):
        """auto ack the  Fail trxs"""
        group_id = self.check_group_id_as_required(group_id)
        tids = [i["Trx"]["TrxId"] for i in self.pubqueue(group_id) if i["State"] == "FAIL"]
        return self.ack(tids)

    ################ content apis ################
    def get_trx(self, trx_id: str, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/trx/{group_id}/{trx_id}")

    def _update_profile(self, trx):
        return self._post("/api/v1/group/profile", trx)

    def _post_trx(self, trx):
        return self._post("/api/v1/group/content", trx)

    def get_group_content(
        self,
        group_id=None,
        num: int = 20,
        trx_id: str = None,
        reverse: bool = False,
        includestarttrx: bool = False,
        senders: List = None,
    ) -> List:
        """requests the content trxs of a group,return the list of the trxs data.

        按条件获取某个组的内容并去重返回

        reverse: 默认按顺序获取, 如果是 True, 从最新的内容开始获取
        trx_id: 某条内容的 Trx ID, 如果提供, 从该条之后(不包含)获取
        num: 要获取内容条数, 默认获取最前面的 20 条内容
        includestarttrx: 如果是 True, 获取内容包含 Trx ID 这条内容
        """
        try:
            group_id = self.check_group_joined_as_required(group_id)
        except:
            return []
        params = {
            "num": num,
            "reverse": reverse,
        }
        if trx_id:
            params["starttrx"] = trx_id
            params["includestarttrx"] = includestarttrx
        if senders:
            params["senders"] = senders
        endpoint = f"/app/api/v1/group/{group_id}/content"
        apiurl = utils.get_url(None, endpoint, is_quote=False, **params)
        trxs = self._post(apiurl) or []
        return utils.unique_trxs(trxs)

    ################ appconfig apis ################
    def keylist(self, group_id=None):
        """get the keylist of the group appconfig"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/appconfig/keylist")

    def key(self, key: str, group_id=None):
        """get the key value of the group appconfig by keyname"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/appconfig/{key}")

    def trx_mode(self, trx_type: str = "POST", group_id=None):
        """get the trx mode of trx type
        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
        "BLOCK_SYNCED","BLOCK_PRODUCED" or "ASK_PEERID"
        """
        group_id = self.check_group_id_as_required(group_id)
        trx_type = utils.check_trx_type(trx_type)
        return self._get(f"/api/v1/group/{group_id}/trx/auth/{trx_type}")

    @property
    def mode(self):
        """get the trx mode of all the trx types"""
        rlt = {}
        for itype in TRX_TYPES:
            resp = self.trx_mode(itype)
            rlt[resp["TrxType"]] = resp["AuthType"]
        return rlt

    def set_trx_mode(
        self,
        trx_type: str,
        mode: str,
        memo: str = "set trx auth type",
        group_id=None,
    ):
        """set the trx mode of trx type
        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" or "ASK_PEERID"
        mode:
            alw "follow_alw_list"
            dny "follow_dny_list"
        """
        group_id = self.check_group_owner_as_required(group_id)
        mode = utils.check_trx_mode(mode)
        trx_type = utils.check_trx_type(trx_type)
        payload = {
            "group_id": group_id,
            "type": "set_trx_auth_mode",
            "config": json.dumps({"trx_type": trx_type, "trx_auth_mode": f"follow_{mode}_list"}),
            "Memo": memo,
        }
        return self._post("/api/v1/group/chainconfig", payload)

    def _update_list(
        self,
        pubkey: str,
        mode: str,
        memo: str = "update list",
        action: str = "add",
        trx_types: List = None,
        group_id=None,
    ):
        """update the list for the trx mode"""
        group_id = self.check_group_owner_as_required(group_id)
        mode = utils.check_trx_mode(mode)
        trx_types = trx_types or ["post"]
        trx_types = [utils.check_trx_type(trx_type) for trx_type in trx_types]
        if action not in ["add", "remove"]:
            raise ValueError("action must be add or remove")
        _params = {"action": action, "pubkey": pubkey, "trx_type": trx_types}
        payload = {
            "group_id": group_id,
            "type": f"upd_{mode}_list",
            "config": json.dumps(_params),
            "Memo": memo,
        }
        return self._post("/api/v1/group/chainconfig", payload)

    def add_allow_list(self, pubkey: str, trx_types: List = None, group_id=None):
        """add pubkey to allow list of trx types"""
        group_id = self.check_group_owner_as_required(group_id)
        return self._update_list(
            pubkey,
            mode="alw",
            memo="add allow list",
            action="add",
            trx_types=trx_types,
            group_id=group_id,
        )

    def remove_allow_list(self, pubkey: str, trx_types: List = None, group_id=None):
        """remove pubkey from allow list of trx types"""
        return self._update_list(
            pubkey,
            mode="alw",
            memo="remove allow list",
            action="remove",
            trx_types=trx_types,
            group_id=group_id,
        )

    def add_deny_list(self, pubkey: str, trx_types: List = None, group_id=None):
        """add pubkey to deny list of trx types"""
        group_id = self.check_group_owner_as_required(group_id)
        return self._update_list(
            pubkey,
            mode="dny",
            memo="add deny list",
            action="add",
            trx_types=trx_types,
            group_id=group_id,
        )

    def remove_deny_list(self, pubkey: str, trx_types: List = None, group_id=None):
        """remove pubkey from deny list of trx types"""
        return self._update_list(
            pubkey,
            mode="dny",
            memo="remove deny list",
            action="remove",
            trx_types=trx_types,
            group_id=group_id,
        )

    def _get_list(self, mode: str, group_id=None) -> List:
        if mode not in ["allow", "deny"]:
            raise ParamValueError("mode must be one of these: allow,deny")
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/trx/{mode}list") or []

    def get_allow_list(self, group_id=None):
        """get allow list"""
        return self._get_list("allow", group_id)

    def get_deny_list(self, group_id=None):
        """get deny list"""
        return self._get_list("deny", group_id)

    def _update_appconfig(
        self,
        key_name,
        key_type,
        key_value,
        action="add",
        memo=None,
        group_id=None,
    ):
        group_id = self.check_group_owner_as_required(group_id)
        if action.lower() not in ["add", "remove"]:
            raise ParamValueError("action must be add or remove")

        payload = {
            "action": action,
            "group_id": group_id,
            "name": key_name,
            "type": key_type,
            "value": key_value,
            "memo": memo or f"update {key_name}",
        }
        return self._post("/api/v1/group/appconfig", payload)

    def set_group_desc(self, desc: str, group_id=None):
        """set group description as appconfig"""
        payload = {
            "key_name": "group_desc",
            "key_type": "string",
            "key_value": desc,
            "action": "add",
            "memo": "set group desc",
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_icon(self, icon, group_id=None):
        """set group icon as appconfig"""
        payload = {
            "key_name": "group_icon",
            "key_type": "string",
            "key_value": utils.group_icon(icon),
            "action": "add",
            "memo": "set group icon",
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_announcement(self, announcement, group_id=None):
        """set group announcement as appconfig"""
        payload = {
            "key_name": "group_announcement",
            "key_type": "string",
            "key_value": announcement,
            "action": "add",
            "memo": "set group announcement",
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_default_permission(self, default_permission, group_id=None):
        """set group default permission as appconfig
        default_permission: WRITE or READ"""
        if default_permission.upper() not in ["WRITE", "READ"]:
            raise ParamValueError("default_permission must be one of these: WRITE,READ")
        payload = {
            "key_name": "group_default_permission",
            "key_type": "string",
            "key_value": default_permission.upper(),
            "action": "add",
            "memo": "set group default permission",
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    ################ announce api ################

    def _announce(self, action, announce_type, memo, group_id=None):
        """announce user or producer, only for self
        action: "add" or "remove"
        announce_type: "user" or "producer"
        """
        group_id = self.check_group_id_as_required(group_id)
        if action.lower() not in ["add", "remove"]:
            raise ParamValueError("action must be one of these: add, remove")
        if announce_type.lower() not in ["user", "producer"]:
            raise ParamValueError("announce_type must be one of these: user, producer")
        payload = {
            "group_id": group_id,
            "action": action,
            "type": announce_type,
            "memo": memo,
        }
        return self._post("/api/v1/group/announce", payload)

    ################ private group users apis ################

    def announce_as_user(self, group_id=None):
        """announce as user"""
        return self._announce("add", "user", "announce self as user", group_id=group_id)

    def get_announced_users(self, group_id=None):
        """get the announced users to approve(add or remove)"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/users")

    def is_announced_user(self, pubkey, group_id=None):
        """check the user is announced or not"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/user/{pubkey}")

    def _approve_user(self, pubkey, action="add", group_id=None):
        """update the user of the group
        action: "add" or "remove"
        """
        group_id = self.check_group_owner_as_required(group_id)
        if action.lower() not in ["add", "remove"]:
            raise ParamValueError("action must be one of these: add, remove")
        payload = {
            "user_pubkey": pubkey,
            "group_id": group_id,
            "action": action,
        }
        return self._post("/api/v1/group/user", payload)

    def add_user(self, pubkey, group_id=None):
        """add pubkey as group user to the group"""
        try:
            status = self.is_announced_user(pubkey)
            if status.get("Result") == "APPROVED":
                return status
        except:
            pass
        return self._approve_user(pubkey, action="add", group_id=group_id)

    def remove_user(self, pubkey, group_id=None):
        """remove pubkey as group user from the group"""
        return self._approve_user(pubkey, action="remove", group_id=group_id)

    ################ producer apis ################

    def announce_as_producer(self, group_id=None):
        """announce as producer"""
        group_id = self.check_group_id_as_required(group_id)
        return self._announce("add", "producer", "announce self as producer", group_id)

    def announce_as_producer_to_remove(self, group_id=None):
        """announce as producer to remove"""
        group_id = self.check_group_id_as_required(group_id)
        return self._announce("remove", "producer", "announce self as producer to remove", group_id)

    def producers(self, group_id=None):
        """get the producers of the group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/producers")

    def get_announced_producers(self, group_id=None):
        """get the announced producers to be approved"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/producers")

    def _update_producer(self, pubkeys: List, action: str, group_id=None):
        """Only group owner can update producers: add, or remove.
        action: "add" or "remove"
        """
        group_id = self.check_group_owner_as_required(group_id)
        action = action.lower()
        if action not in ("add", "remove"):
            raise ParamValueError("action should be `add` or `remove`")
        payload = {
            "producer_pubkey": pubkeys,
            "group_id": group_id,
            "action": action,
        }
        return self._post("/api/v1/group/producer", payload)

    def add_producer(self, pubkeys: List, group_id=None):
        """add pubkey as group producer to the group"""
        return self._update_producer(pubkeys, action="add", group_id=group_id)

    def remove_producer(self, pubkeys, group_id=None):
        """remove pubkey as group producer from the group"""
        return self._update_producer(pubkeys, action="remove", group_id=group_id)
