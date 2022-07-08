import base64
import datetime
import json
import logging
import os
import time
import urllib
from typing import Any, Dict, List

import filetype

import rumpy.utils as utils
from rumpy.api.base import BaseAPI
from rumpy.exceptions import *
from rumpy.types.data import *

logger = logging.getLogger(__name__)


class FullNodeAPI(BaseAPI):
    @property
    def node_info(self):
        """return node info, dataclasses.dataclass type"""
        resp = self._get("/api/v1/node")
        return NodeInfo(**resp)

    @property
    def node_id(self) -> str:
        """return node_id of this node"""
        return self.node_info.node_id

    @property
    def node_pubkey(self) -> str:
        """return pubkey of this node; be attention: node will get different pubkey in groups"""
        return self.node_info.node_publickey

    @property
    def node_status(self) -> str:
        """return status of this node; unknown, online or offline"""
        return self.node_info.node_status

    @property
    def peers(self) -> Dict:
        """return dict of different peers which this node has connected"""
        return self.node_info.peers

    def connect(self, peers: List):
        """直连指定节点

        peers = [
            "/ip4/94.23.17.189/tcp/10666/p2p/16Uiu2HAmGTcDnhj3KVQUwVx8SGLyKBXQwfAxNayJdEwfsnUYKK4u"
            ]
        """
        return self._post("/api/v1/network/peers", peers)

    def get_peers(self):
        """获取能 ping 通的节点"""
        return self._get("/api/v1/network/peers/ping")

    def psping(self, peer_id: str):
        """ping 一个节点

        peer_id: 节点 ID, 例如 "16Uiu2HAxxxxxx...xxxxzEYBnEKFnao"
        """
        return self._post("/api/v1/psping", {"peer_id": peer_id})

    @property
    def network(self) -> Dict:
        """return network info of this node"""
        return self._get("/api/v1/network")

    @property
    def node_eth_addr(self):
        return self.network.get("eth_addr")

    def _groups(self) -> List:
        """return list of group info which node has joined"""
        return self._get("/api/v1/groups")

    def backup(self):
        """Backup my group seed/keystore/config"""
        return self._get("/api/v1/backup")

    def token(self):
        """Get a auth token for authorizing requests from remote"""
        return self._post("/app/api/v1/token/apply")

    def token_refresh(self):
        """Get a new auth token"""
        return self._post("/app/api/v1/token/refresh")

    def network_stats(self, start: str = None, end: str = None):
        """Get network stats summary

        param: start/end, str, query, "2022-04-28" or "2022-04-28 10:00" or "2022-04-28T10:00Z08:00"
        """
        api = utils.get_url(None, "/api/v1/network/stats", is_quote=True, start=start, end=end)
        return self._get(api)

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
                403,
                "consensus_type should be `poa` or `pos` or `pow`, but only `poa` is supported now.",
            )

        payload = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }

        seed = self._post("/api/v1/group", payload)
        return seed  # utils.check_seed(seed)

    def seed(self, group_id=None) -> Dict:
        """get the seed of a group which you've joined in."""
        group_id = self.check_group_id_as_required(group_id)
        seed = self._get(f"/api/v1/group/{group_id}/seed")
        return seed  # utils.check_seed(seed)

    def group_info(self, group_id=None):
        """return group info,type: datacalss"""
        group_id = self.check_group_joined_as_required(group_id)
        info = {}
        for _info in self.groups():
            if _info["group_id"] == group_id:
                info = _info
                break
        info["snapshot_info"] = info.get("snapshot_info", {})
        return GroupInfo(**info)

    @property
    def pubkey(self):
        return self.group_info().user_pubkey

    @property
    def owner(self):
        return self.group_info().owner_pubkey

    @property
    def eth_addr(self):
        return self.group_info().user_eth_addr

    def join_group(self, seed: Dict, v=1):
        """join a group with the seed of the group"""

        # seed = utils.check_seed(seed)
        # 兼容新版本 seed
        if type(seed) == str and seed.startswith("rum://seed?"):
            seed = {"seed": seed}
        resp = self._post(f"/api/v{v}/group/join", seed)
        return resp  # self.raise_error(resp, "Group with same GroupId existed")

    def leave_group(self, group_id=None):
        """leave a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post("/api/v1/group/leave", {"group_id": group_id})

    def clear_group(self, group_id=None):
        """clear data of a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post("/api/v1/group/clear", {"group_id": group_id})

    def startsync(self, group_id=None):
        """触发同步"""
        group_id = self.check_group_id_as_required(group_id)
        return self._post(f"/api/v1/group/{group_id}/startsync")

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

    def _send(self, activity_type=None, group_id=None, obj=None, **kwargs) -> Dict:
        group_id = self.check_group_joined_as_required(group_id)
        payload = NewTrx(group_id=group_id, obj=obj, activity_type=activity_type, **kwargs).__dict__
        return self._post("/api/v1/group/content", payload)

    def block(self, block_id: str, group_id=None):
        """get the info of a block in a group"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/block/{group_id}/{block_id}")

    def get_trx(self, trx_id: str, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/trx/{group_id}/{trx_id}")

    def pubqueue(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        resp = self._get(f"/api/v1/group/{group_id}/pubqueue")
        return resp.get("Data")

    def ack(self, trx_ids: List):
        return self._post("/api/v1/trx/ack", {"trx_ids": trx_ids})

    def autoack(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        tids = [i["Trx"]["TrxId"] for i in self.pubqueue(group_id) if i["State"] == "FAIL"]
        return self.ack(tids)

    def trx_mode(self, trx_type: str = "POST", group_id=None):
        """获取某个 trx 类型的授权方式

        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        group_id = self.check_group_id_as_required(group_id)
        trx_type = utils.check_trx_type(trx_type)
        return self._get(f"/api/v1/group/{group_id}/trx/auth/{trx_type}")

    @property
    def mode(self):
        """获取所有 trx 类型的授权方式"""
        rlt = {}
        for itype in TRX_TYPES:
            resp = self.trx_mode(itype)
            rlt[resp["TrxType"]] = resp["AuthType"]
        return rlt

    def set_mode(self, mode, group_id=None):
        """将所有 trx 类型设置为一种授权方式

        mode: 授权方式, "follow_alw_list"(白名单方式), "follow_dny_list"(黑名单方式)
        """
        group_id = self.check_group_owner_as_required(group_id)
        mode = utils.check_trx_mode(mode)
        for itype in TRX_TYPES:
            self.set_trx_mode(itype, mode, f"{itype} set mode to {mode}", group_id=group_id)

    def set_trx_mode(
        self,
        trx_type: str,
        mode: str,
        memo: str = "set trx auth type",
        group_id=None,
    ):
        """设置某个 trx 类型的授权方式

        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        mode: 授权方式, "follow_alw_list"(白名单方式), "follow_dny_list"(黑名单方式)
        memo: Memo
        """
        group_id = self.check_group_owner_as_required(group_id)
        mode = utils.check_trx_mode(mode)

        trx_type = utils.check_trx_type(trx_type)
        if not memo:
            raise ParamValueError("say something in param:memo")

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
        trx_types: List = None,
        group_id=None,
    ):
        group_id = self.check_group_owner_as_required(group_id)
        mode = utils.check_trx_mode(mode)

        trx_types = trx_types or ["post"]
        for trx_type in trx_types:
            utils.check_trx_type(trx_type)

        _params = {"action": "add", "pubkey": pubkey, "trx_type": trx_types}
        payload = {
            "group_id": group_id,
            "type": f"upd_{mode}_list",
            "config": json.dumps(_params),
            "Memo": memo,
        }
        return self._post("/api/v1/group/chainconfig", payload)

    def update_allow_list(
        self,
        pubkey: str,
        memo: str = "update allow list",
        trx_types: List = None,
        group_id=None,
    ):
        """将某个用户加入某个/某些 trx 类型的白名单中

        pubkey: 用户公钥
        memo: Memo
        trx_types: Trx 类型组成的列表, Trx 类型有 "POST","ANNOUNCE",
            "REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        group_id = self.check_group_owner_as_required(group_id)
        return self._update_list(pubkey, "alw", memo, trx_types, group_id)

    def update_deny_list(
        self,
        pubkey: str,
        memo: str = "update deny list",
        trx_types: List = None,
        group_id=None,
    ):
        """将某个用户加入某个/某些 trx 类型的黑名单中

        pubkey: 用户公钥
        memo: Memo
        trx_types: Trx 类型组成的列表, Trx 类型有 "POST","ANNOUNCE",
            "REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        group_id = self.check_group_owner_as_required(group_id)
        return self._update_list(pubkey, "dny", memo, trx_types, group_id)

    def _list(self, mode: str, group_id=None) -> List:
        if mode not in ["allow", "deny"]:
            raise ParamValueError("mode must be one of these: allow,deny")
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/trx/{mode}list") or []

    @property
    def allow_list(self):
        """获取某个组的白名单"""
        return self._list("allow")

    @property
    def deny_list(self):
        """获取某个组的黑名单"""
        return self._list("deny")

    def get_allow_list(self, group_id=None):
        """获取某个组的白名单"""
        return self._list("allow", group_id)

    def get_deny_list(self, group_id=None):
        """获取某个组的黑名单"""
        return self._list("deny", group_id)

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

        payload = {
            "action": action,
            "group_id": group_id,
            "name": key_name,
            "type": key_type,
            "value": key_value,
            "memo": memo or f"update {key_name}",
        }
        return self._post("/api/v1/group/appconfig", payload)

    def set_group_desc(self, desc: str, action="add", memo=None, group_id=None):
        payload = {
            "key_name": "group_desc",
            "key_type": "string",
            "key_value": desc,
            "action": action,
            "memo": memo,
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_icon(self, icon, action="add", memo=None, group_id=None):
        payload = {
            "key_name": "group_icon",
            "key_type": "string",
            "key_value": utils.group_icon(icon),
            "action": action,
            "memo": memo,
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_announcement(self, announcement, action="add", memo=None, group_id=None):
        payload = {
            "key_name": "group_announcement",
            "key_type": "string",
            "key_value": announcement,
            "action": action,
            "memo": memo,
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_group_default_permission(self, default_permission, action="add", memo=None, group_id=None):
        payload = {
            "key_name": "group_default_permission",
            "key_type": "string",
            "key_value": default_permission,  # WRITE or READ
            "action": action,
            "memo": memo,
            "group_id": group_id,
        }
        return self._update_appconfig(**payload)

    def set_appconfig(
        self,
        desc: str = None,
        icon=None,
        announcement: str = None,
        default_permission: str = None,
        action="add",
        memo=None,
        group_id=None,
    ):
        if desc:
            self.set_group_desc(desc, action=action, memo=memo, group_id=group_id)
        if icon:
            self.set_group_icon(icon, action=action, memo=memo, group_id=group_id)
        if announcement:
            self.set_group_announcement(announcement, action=action, memo=memo, group_id=group_id)
        if default_permission:
            self.set_group_default_permission(default_permission, action=action, memo=memo, group_id=group_id)

    def keylist(self, group_id=None):
        """获取组的所有配置项"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/appconfig/keylist")

    def key(self, key: str, group_id=None):
        """获取组的某个配置项的信息

        key: 配置项名称
        """
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/appconfig/{key}")

    def announce(self, action="add", type="user", memo="rumpy.api", group_id=None):
        """announce user or producer,add or remove

        申请 成为/退出 producer/user

        action: "add" 或 "remove", 申请成为/宣布退出
        type: "user" 或 "producer"
        memo: Memo
        """
        group_id = self.check_group_id_as_required(group_id)
        payload = {
            "group_id": group_id,
            "action": action,  # add or remove
            "type": type,  # user or producer
            "memo": memo,
        }
        return self._post("/api/v1/group/announce", payload)

    def announce_as_user(self, group_id=None):
        """announce self as user

        申请成为私有组用户

        如果已经是用户, 返回申请状态
        """
        status = self.announced_user(self.pubkey)
        # TODO:如果 pubkey 没有被 announced ，会有个 400 的 chain 的报错，需要封装下
        if status.get("Result") == "APPROVED":
            return status
        return self.announce("add", "user", "rumpy.api,announce self as user", group_id)

    def announce_as_producer(self, group_id=None):
        """announce self as producer"""
        return self.announce("add", "producer", "rumpy.api,announce self as producer", group_id)

    def announced_producers(self, group_id=None):
        """获取申请 成为/退出 的 producers"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/producers")

    def announced_users(self, group_id=None):
        """获取申请 成为/退出 的 users"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/users")

    def announced_user(self, pubkey, group_id=None):
        """获取申请 成为/退出 的 user 的申请状态

        pubkey: 用户公钥
        """
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/announced/user/{pubkey}")

    def producers(self, group_id=None):
        """获取已经批准的 producers"""
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/api/v1/group/{group_id}/producers")

    def update_user(self, pubkey, action="add", group_id=None):
        """组创建者添加或移除私有组用户

        action: "add" or "remove"
        """
        group_id = self.check_group_owner_as_required(group_id)
        payload = {
            "user_pubkey": pubkey,
            "group_id": group_id,
            "action": action,  # "add" or "remove"
        }
        return self._post("/api/v1/group/user", payload)

    def approve_as_user(self, pubkey=None, group_id=None):  # TODO:这几个 用户 全选管理的方法 从语义的角落来看，挺臃肿的，待修改。
        """approve pubkey as a user of group.

        pubkey: 用户公钥, 如果不提供该参数, 默认将 owner 自己添加为私有组用户
        """
        return self.update_user(pubkey=pubkey or self.pubkey, group_id=group_id)

    def update_producer(self, pubkey=None, group_id=None, action="add"):
        """Only group owner can update producers: add, or remove.

        pubkey: the producer's pubkey
        action: "add" or "remove"
        """
        group_id = self.check_group_owner_as_required(group_id)
        action = action.lower()
        if action not in ("add", "remove"):
            raise ParamValueError("action should be `add` or `remove`")
        payload = {
            "producer_pubkey": pubkey,
            "group_id": group_id,
            "action": action,
        }
        return self._post("/api/v1/group/producer", payload)

    def update_profile(self, name=None, image=None, mixin_id=None, group_id=None):
        """user update the profile: name, image, or wallet.

        name: nickname of user
        image: one image, as file_path or bytes or bytes-string
        mixin_id: one kind of wallet
        """
        group_id = self.check_group_joined_as_required(group_id)
        obj = PersonObj(name=name, image=image, wallet={"wallet_id": mixin_id})
        payload = NewTrx(activity_type="Update", group_id=group_id, obj=obj).__dict__
        return self._post("/api/v1/group/profile", payload)

    def pubkey_to_addr(self, pubkey):
        payload = {"encoded_pubkey": pubkey}
        resp = self._post("/api/v1/tools/pubkeytoaddr", payload)
        if addr := resp.get("addr"):
            return addr
        else:
            raise ParamValueError(f"pubkey_to_addr failed. pubkey:{pubkey},resp: {resp}")

    def ask_for_relay(self, reley_ips: List):
        """owner in private network ask for relay servers

        Args:
            reley_ips (List): ["/ip4/10x.xx.xxx.xxx/tcp/31124/ws/p2p/16Uiu2H...uisLB""]
        {'ok': True}
        """
        return self._post("/api/v1/network/relay", reley_ips)
