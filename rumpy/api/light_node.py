import json
import logging
from typing import Any, Dict, List

from rumpy.api.base import BaseAPI
from rumpy.exceptions import *
from rumpy.types.data import NewTrx, PersonObj

logger = logging.getLogger(__name__)


class LightNodeAPI(BaseAPI):
    def quit(self):
        return self._get("/quit")

    def __create_alias_of_key(self, alias: str, key_type: str):
        if key_type not in ("sign", "encrypt"):
            raise ParamValueError(403, "key_type must be one of `sign`, `encrypt`.")
        payload = {"alias": alias, "type": key_type}
        return self._post("/v1/keystore/create", payload)

    def create_alias_of_sign_key(self, alias="my_signe"):
        return self.__create_alias_of_key(alias, "sign")

    def create_alias_of_encrypt_key(self, alias="my_encrypt"):
        # """需要环境变量 RUM_KSPASSWD"""
        # if not os.getenv("RUM_KSPASSWD"):
        #    raise RumChainException(500, "need RUM_KSPASSWD")
        return self.__create_alias_of_key(alias, "encrypt")

    def create_keypair(self, alias_piece="my"):
        self.create_alias_of_sign_key(alias_piece + "_sign")
        self.create_alias_of_encrypt_key(alias_piece + "_encrypt")

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
        seed: Dict,
        sign_alias: str = None,
        encrypt_alias: str = None,
        urls: List = None,
        pair_alias=None,
    ):
        if pair_alias:
            sign_alias = pair_alias + "_sign"
            encrypt_alias = pair_alias + "_encrypt"
        payload = {
            "seed": seed,
            "sign_alias": sign_alias,
            "encrypt_alias": encrypt_alias,
            "urls": urls,
        }
        return self._post("/v1/group/join", payload)

    def update_apihosts(self, group_id, urls):
        payload = {
            "group_id": group_id,
            "urls": urls,
        }
        return self._post("/v1/group/apihosts", payload)

    def leave_group(self, group_id):
        payload = {
            "group_id": group_id,
        }
        return self._post("/v1/group/leave", payload)

    def _groups(self):
        return self._get("/v1/group/listall")

    def group(self, group_id):
        return self._get(f"/v1/group/{group_id}/list")

    def group_info(self, group_id):
        return self._get(f"/v1/group/{group_id}/info")

    def seed(self, group_id):
        return self._get(f"/v1/group/{group_id}/seed")

    def trx(self, group_id, trx_id):
        return self._get(f"/v1/trx/{group_id}/{trx_id}")

    def block(self, group_id, block_id):
        return self._get(f"/v1/block/{group_id}/{block_id}")

    def producers(self, group_id):
        return self._get(f"/v1/group/{group_id}/producers")

    def users(self, group_id):
        return self._get(f"/v1/group/{group_id}/announced/users")

    def user(self, group_id, pubkey):
        return self._get(f"/v1/group/{group_id}/announced/user/{pubkey}")

    def appconfig_keylist(self, group_id):
        return self._get(f"/v1/group/{group_id}/appconfig/keylist")

    def appconfig_key(self, group_id, key):
        return self._get(f"/v1/group/{group_id}/appconfig/{key}")

    def get_group_content(
        self,
        group_id: str,
        reverse: bool = False,
        trx_id: str = None,
        num: int = 20,
        includestarttrx: bool = False,
        senders: List = None,
    ) -> List:

        payload = {
            "group_id": group_id,
            "num": num,
            "start_trx": trx_id,
            "reverse": json.dumps(reverse),
            "include_start_trx": json.dumps(includestarttrx),
            "senders": senders,
        }

        return self._post(f"/v1/group/getctn", payload)

    def _send(self, activity_type=None, group_id=None, obj=None, **kwargs) -> Dict:
        payload = NewTrx(group_id=group_id, activity_type=activity_type, obj=obj, **kwargs).__dict__
        return self._post("/v1/group/content", payload)

    def update_profile(self, group_id, name=None, mixin_id=None, image=None):
        """user update the profile: name, image, or wallet.

        name: nickname of user
        image: one image, as file_path or bytes or bytes-string
        mixin_id: one kind of wallet
        """
        obj = PersonObj(name=name, image=image, wallet={"wallet_id": mixin_id})
        payload = NewTrx(activity_type="Update", group_id=group_id, obj=obj).__dict__
        return self._post(f"/v1/group/profile", payload)
