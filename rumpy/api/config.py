import json
import base64
from typing import List, Dict, Any
from rumpy.api.base import BaseAPI
from rumpy.api.group import Group
from rumpy.types.data import *
from rumpy.utils import zip_image_file
import logging

logger = logging.getLogger(__name__)


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

    def trx_mode(self, trx_type: str = "POST"):
        """获取某个 trx 类型的授权方式

        trx_type: "POST","ANNOUNCE","REQ_BLOCK_FORWARD","REQ_BLOCK_BACKWARD",
            "BLOCK_SYNCED","BLOCK_PRODUCED" 或 "ASK_PEERID"
        """
        trx_type = self._check_trx_type(trx_type)
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
        self._check_owner()
        mode = self._check_mode(mode)
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
        self._check_owner()
        mode = self._check_mode(mode)

        trx_type = self._check_trx_type(trx_type)
        if not memo:
            raise ValueError("say something in param:memo")

        relay = {
            "group_id": self.group_id,
            "type": "set_trx_auth_mode",
            "config": json.dumps({"trx_type": trx_type, "trx_auth_mode": f"follow_{mode}_list"}),
            "Memo": memo,
        }
        return self._post("/group/chainconfig", relay)

    def _update_list(
        self,
        pubkey: str,
        mode: str,
        memo: str = "update list",
        trx_types: List = None,
    ):
        self._check_owner()
        mode = self._check_mode(mode)

        trx_types = trx_types or ["post"]
        for trx_type in trx_types:
            self._check_trx_type(trx_type)

        relay = {
            "group_id": self.group_id,
            "type": f"upd_{mode}_list",
            "config": json.dumps({"action": "add", "pubkey": pubkey, "trx_type": trx_types}),
            "Memo": memo,
        }
        return self._post("/group/chainconfig", relay)

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
        self._check_owner()
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
        self._check_owner()
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

    def group_icon(self, file_path):
        """将一张图片处理成组配置项 value 字段的值, 例如组的图标对象"""
        import filetype

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
        relay = {
            "action": action,
            "group_id": self.group_id,
            "name": name,
            "type": the_type,
            "value": value,
            "memo": memo,
        }
        self._check_owner()

        return self._post("/group/appconfig", relay)

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
        self._check_group_id()
        relay = {
            "group_id": self.group_id,
            "action": action,  # add or remove
            "type": type,  # user or producer
            "memo": memo,
        }
        return self._post("/group/announce", relay)

    def announce_as_user(self):
        """announce self as user

        申请成为私有组用户

        如果已经是用户, 返回申请状态
        """
        status = self.announced_user(self.group.pubkey)
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

    def update_user(self, user_pubkey, action="add"):
        """组创建者添加或移除私有组用户

        user_pubkey: 用户公钥
        action: "add" 或 "remove", 添加或移除
        """
        self._check_group_id()
        self._check_owner()
        relay = {
            "user_pubkey": user_pubkey,
            "group_id": self.group_id,
            "action": action,  # "add" or "remove"
        }
        return self._post("/group/user", relay)

    def approve_as_user(self, pubkey=None):
        """添加私有组用户

        pubkey: 用户公钥, 如果不提供该参数, 默认将 owner 自己添加为私有组用户
        """
        return self.update_user(user_pubkey=pubkey or self.group.pubkey)

    def update_producer(self, pubkey=None, group_id=None, action="add"):
        """组创建者添加或移除 producer

        pubkey: producer 公钥
        group_id: 组 ID
        action: "add" 或 "remove", 添加或移除
        """
        self._check_owner()
        action = action.lower()
        if action not in ("add", "remove"):
            raise ValueError("action should be `add` or `remove`")
        relay = {
            "producer_pubkey": pubkey,
            "group_id": group_id or self.group_id,
            "action": action,
        }
        return self._post("/group/producer", relay)

    def update_profile(self, name, image=None, mixin_id=None):
        """更新组的用户配置, 以 rum-app 为例, 如昵称, 头像, 绑定钱包(以 mixin 钱包为例)

        name: 昵称
        image: 头像, 图片的路径, rum-app 设有默认头像, 不提供, 将使用默认头像更新
        mixin_id: mixin 账号 uuid, 目前 rum-app 支持的钱包, 可选
        """
        if image is not None:
            image = NewTrxImg(file_path=image).__dict__
        relay = {
            "type": "Update",
            "person": {"name": name, "image": image},
            "target": {"id": self.group_id, "type": "Group"},
        }
        if mixin_id is not None:
            relay["person"]["wallet"] = {
                "id": mixin_id,
                "type": "mixin",
                "name": "mixin messenger",
            }
        return self._post("/group/profile", relay)
