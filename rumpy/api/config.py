import base64
import json
import logging
import filetype
from typing import Any, Dict, List

from rumpy.api.base import BaseAPI
from rumpy.api.group import Group
from rumpy.types.data import *
from rumpy.utils import zip_image_file

logger = logging.getLogger(__name__)


def _check_mode(mode: str):
    if mode.lower() not in ["dny", "deny", "allow", "alw"]:
        raise ValueError(f"{mode} mode must be one of ['deny','allow']")
    if mode.lower() in ["dny", "deny"]:
        return "dny"
    if mode.lower() in ["alw", "allow"]:
        return "alw"


def _check_trx_type(trx_type: str):
    if trx_type.upper() not in TRX_TYPES:
        raise ValueError(f"{trx_type} must be one of {TRX_TYPES}")
    return trx_type.lower()


class GroupConfig(BaseAPI):
    """config apis/methods for chainconfig, appconfig, user profile config.

    Args:
        BaseAPI (class): base class of rumpy api.
    """

    def trx_mode(self, trx_type: str = "POST"):
        """获取某个 trx 类型的授权方式

        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        trx_type = _check_trx_type(trx_type)
        return self._get(f"/group/{self.group_id}/trx/auth/{trx_type}")

    @property
    def mode(self):
        """获取所有 trx 类型的授权方式"""
        rlt = {}
        for itype in TRX_TYPES:
            resp = self.trx_mode(itype)
            rlt[resp["TrxType"]] = resp["AuthType"]
        return rlt

    def set_mode(self, mode):
        """将所有 trx 类型设置为一种授权方式

        mode: 授权方式, "follow_alw_list"(白名单方式), "follow_dny_list"(黑名单方式)
        """
        self.check_group_owner_as_required()
        mode = _check_mode(mode)
        for itype in TRX_TYPES:
            self.set_trx_mode(itype, mode, f"{itype} set mode to {mode}")

    def set_trx_mode(
        self,
        trx_type: str,
        mode: str,
        memo: str = "set trx auth type",
    ):
        """设置某个 trx 类型的授权方式

        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        mode: 授权方式, "follow_alw_list"(白名单方式), "follow_dny_list"(黑名单方式)
        memo: Memo
        """
        self.check_group_owner_as_required()
        mode = _check_mode(mode)

        trx_type = _check_trx_type(trx_type)
        if not memo:
            raise ValueError("say something in param:memo")

        payload = {
            "group_id": self.group_id,
            "type": "set_trx_auth_mode",
            "config": json.dumps({"trx_type": trx_type, "trx_auth_mode": f"follow_{mode}_list"}),
            "Memo": memo,
        }
        return self._post("/group/chainconfig", payload)

    def _update_list(
        self,
        pubkey: str,
        mode: str,
        memo: str = "update list",
        trx_types: List = None,
    ):
        self.check_group_owner_as_required()
        mode = _check_mode(mode)

        trx_types = trx_types or ["post"]
        for trx_type in trx_types:
            _check_trx_type(trx_type)

        _params = {"action": "add", "pubkey": pubkey, "trx_type": trx_types}
        payload = {
            "group_id": self.group_id,
            "type": f"upd_{mode}_list",
            "config": json.dumps(_params),
            "Memo": memo,
        }
        return self._post("/group/chainconfig", payload)

    def update_allow_list(
        self,
        pubkey: str,
        memo: str = "update allow list",
        trx_types: List = None,
    ):
        """将某个用户加入某个/某些 trx 类型的白名单中

        pubkey: 用户公钥
        memo: Memo
        trx_types: Trx 类型组成的列表, Trx 类型有 "POST","ANNOUNCE",
            "REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        self.check_group_owner_as_required()
        return self._update_list(pubkey, "alw", memo, trx_types)

    def update_deny_list(
        self,
        pubkey: str,
        memo: str = "update deny list",
        trx_types: List = None,
    ):
        """将某个用户加入某个/某些 trx 类型的黑名单中

        pubkey: 用户公钥
        memo: Memo
        trx_types: Trx 类型组成的列表, Trx 类型有 "POST","ANNOUNCE",
            "REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        self.check_group_owner_as_required()
        return self._update_list(pubkey, "dny", memo, trx_types)

    def _list(self, mode: str) -> List:
        if mode not in ["allow", "deny"]:
            raise ValueError("mode must be one of these: allow,deny")

        return self._get(f"/group/{self.group_id}/trx/{mode}list") or []

    @property
    def allow_list(self):
        """获取某个组的白名单"""
        return self._list("allow")

    @property
    def deny_list(self):
        """获取某个组的黑名单"""
        return self._list("deny")

    def get_allow_list(self):
        """获取某个组的白名单"""
        return self._list("allow")

    def get_deny_list(self):
        """获取某个组的黑名单"""
        return self._list("deny")

    def group_icon(self, file_path: str):
        """将一张图片处理成组配置项 value 字段的值, 例如组的图标对象"""

        img_bytes = zip_image_file(file_path)
        icon = f'data:{filetype.guess(img_bytes).mime}base64,{base64.b64encode(img_bytes).decode("utf-8")}'

        return icon

    def set_appconfig(
        self,
        name="group_desc",
        the_type="string",
        value="增加组的简介",
        action="add",
        image=None,
        memo="add",
    ):
        """组创建者更新组的某个配置项

        name: 配置项的名称, 自定义, 以 rum-app 为例, 目前支持 'group_announcement'(组的公告),
            'group_desc'(组的简介),'group_icon'(组的图标), 均是 "string" 类型
        the_type: 配置项的类型, 可选值为 "int", "bool", "string"
        value: 配置项的值, 必须与 type 相对应
        action: "add" 或 "del", 增加/修改 或 删除
        image: 一张图片路径, 如果提供, 将转换为 value 的值,
            例如 rum-app 用作组的图标(需要 name 是 'group_icon')
        memo: Memo
        """
        if image is not None:
            value = self.group_icon(image)
        payload = {
            "action": action,
            "group_id": self.group_id,
            "name": name,
            "type": the_type,
            "value": value,
            "memo": memo,
        }
        self.check_group_owner_as_required()

        return self._post("/group/appconfig", payload)

    def keylist(self):
        """获取组的所有配置项"""
        return self._get(f"/group/{self.group_id}/appconfig/keylist")

    def key(self, key: str):
        """获取组的某个配置项的信息

        key: 配置项名称
        """
        return self._get(f"/group/{self.group_id}/appconfig/{key}")

    def announce(self, action="add", type="user", memo="rumpy.api"):
        """announce user or producer,add or remove

        申请 成为/退出 producer/user

        action: "add" 或 "remove", 申请成为/宣布退出
        type: "user" 或 "producer"
        memo: Memo
        """
        self.check_group_id_as_required()
        payload = {
            "group_id": self.group_id,
            "action": action,  # add or remove
            "type": type,  # user or producer
            "memo": memo,
        }
        return self._post("/group/announce", payload)

    def announce_as_user(self):
        """announce self as user

        申请成为私有组用户

        如果已经是用户, 返回申请状态
        """
        status = self.announced_user(self._client.group.pubkey)
        if status.get("Result") == "APPROVED":
            return status
        return self.announce("add", "user", "rumpy.api,announce self as user")

    def announce_as_producer(self):
        """announce self as producer"""
        return self.announce("add", "producer", "rumpy.api,announce self as producer")

    def announced_producers(self):
        """获取申请 成为/退出 的 producers"""
        return self._get(f"/group/{self.group_id}/announced/producers")

    def announced_users(self):
        """获取申请 成为/退出 的 users"""
        return self._get(f"/group/{self.group_id}/announced/users")

    def announced_user(self, pubkey):
        """获取申请 成为/退出 的 user 的申请状态

        pubkey: 用户公钥
        """
        return self._get(f"/group/{self.group_id}/announced/user/{pubkey}")

    def producers(self):
        """获取已经批准的 producers"""
        return self._get(f"/group/{self.group_id}/producers")

    def update_user(self, pubkey, action="add"):
        """组创建者添加或移除私有组用户

        action: "add" or "remove"
        """
        self.check_group_owner_as_required()
        payload = {
            "user_pubkey": pubkey,
            "group_id": self.group_id,
            "action": action,  # "add" or "remove"
        }
        return self._post("/group/user", payload)

    def approve_as_user(self, pubkey=None):
        """approve pubkey as a user of group.

        pubkey: 用户公钥, 如果不提供该参数, 默认将 owner 自己添加为私有组用户
        """
        return self.update_user(pubkey=pubkey or self._client.group.pubkey)

    def update_producer(self, pubkey=None, group_id=None, action="add"):
        """Only group owner can update producers: add, or remove.

        pubkey: the producer's pubkey
        action: "add" or "remove"
        """
        self.check_group_owner_as_required()
        action = action.lower()
        if action not in ("add", "remove"):
            raise ValueError("action should be `add` or `remove`")
        payload = {
            "producer_pubkey": pubkey,
            "group_id": group_id or self.group_id,
            "action": action,
        }
        return self._post("/group/producer", payload)

    def update_profile(self, name, image=None, mixin_id=None):
        """user update the profile: name, image, or wallet.

        name: nickname of user
        image: image file_path
        mixin_id: one kind of wallet
        """

        if image is not None:
            image = NewTrxImg(file_path=image).__dict__
        payload = {
            "type": "Update",
            "person": {"name": name, "image": image},
            "target": {"id": self.group_id, "type": "Group"},
        }
        if mixin_id is not None:
            payload["person"]["wallet"] = {
                "id": mixin_id,
                "type": "mixin",
                "name": "mixin messenger",
            }
        return self._post("/group/profile", payload)
