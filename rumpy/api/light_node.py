import json
import logging
from typing import Any, Dict, List, Union

from rumpy.api.base import BaseAPI
from rumpy.exceptions import *


logger = logging.getLogger(__name__)


class LightNodeAPI(BaseAPI):
    def quit(self):
        return self._get("/quit")

    def __create_alias_of_key(self, alias: str, key_type: str):
        if key_type not in ("sign", "encrypt"):
            raise ParamValueError("key_type must be one of `sign`, `encrypt`.")
        payload = {"alias": alias, "type": key_type}
        return self._post("/v1/keystore/create", payload)

    def create_alias_of_sign_key(self, alias="my_signe"):
        return self.__create_alias_of_key(alias, "sign")

    def create_alias_of_encrypt_key(self, alias="my_encrypt"):
        # """需要环境变量 RUM_KSPASSWD"""
        # if not os.getenv("RUM_KSPASSWD"):
        #    raise RumChainException("need RUM_KSPASSWD")
        return self.__create_alias_of_key(alias, "encrypt")

    def create_keypair(self, alias_piece="my"):
        a = self.create_alias_of_sign_key(alias_piece + "_sign")
        b = self.create_alias_of_encrypt_key(alias_piece + "_encrypt")
        return a, b

    def keys(self):
        return self._get("/v1/keystore/listall")

    def remove_alias(self, alias):
        payload = {"alias": alias}
        return self._post("/v1/keystore/remove", payload)

    def bind_alias(self, alias, keyname, type_str):
        payload = {"alias": alias, "keyname": keyname, "type": type_str}
        return self._post("/v1/keystore/bindalias", payload)

    def join_group(
        self,
        seed: str,
        sign_alias: str = None,
        encrypt_alias: str = None,
        urls: List = None,
        pair_alias=None,
        v=2,
    ):
        if pair_alias:
            sign_alias = pair_alias + "_sign"
            encrypt_alias = pair_alias + "_encrypt"
        if not sign_alias:
            err = "sign_alias is required."
            raise ParamValueError(err)
        if v == 1:  # TODO:等 quorum main 合并了 seed 分支后，需升级该方法
            payload = {
                "seed": seed,
                "sign_alias": sign_alias,
                "encrypt_alias": encrypt_alias,
                "urls": urls,
            }
        elif v == 2:
            payload = {
                "seed": seed,  # TODO:需要对 u 的参数进行检查？
                "sign_alias": sign_alias,
                "encrypt_alias": encrypt_alias,
            }
        return self._post(f"/v{v}/group/join", payload)

    def update_apihosts(self, urls, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        payload = {
            "group_id": group_id,
            "urls": urls,
        }
        return self._post("/v1/group/apihosts", payload)

    def leave_group(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        payload = {
            "group_id": group_id,
        }
        return self._post("/v1/group/leave", payload)

    def _groups(self):
        return self._get("/v1/group/listall")

    def group(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/list")

    def group_info(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/info")

    def seed(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/seed")

    def get_trx(self, trx_id, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/trx/{group_id}/{trx_id}")

    def block(self, block_id, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/block/{group_id}/{block_id}")

    def producers(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/producers")

    def users(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/announced/users")

    def user(self, pubkey, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/announced/user/{pubkey}")

    def appconfig_keylist(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/appconfig/keylist")

    def appconfig_key(self, key, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        return self._get(f"/v1/group/{group_id}/appconfig/{key}")

    def get_group_content(
        self,
        group_id: str = None,
        reverse: bool = False,
        trx_id: str = None,
        num: int = 20,
        includestarttrx: bool = False,
        senders: List = None,
    ) -> List:
        group_id = self.check_group_id_as_required(group_id)
        payload = {
            "group_id": group_id,
            "num": num,
            "start_trx": trx_id,
            "reverse": json.dumps(reverse),
            "include_start_trx": json.dumps(includestarttrx),
            "senders": senders,
        }

        return self._post(f"/v1/group/getctn", payload)

    def _post_trx(self, trx):
        return self._post("/v1/group/content", trx)

    def _update_profile(self, trx):
        return self._post(f"/v1/group/profile", trx)
