import json
import logging
from typing import Any, Dict, List

from rumpy.types.data import NewTrx

logger = logging.getLogger(__name__)


class LightAPI:
    def __init__(self, client=None):
        self._client = client

    def create_sign(self, alias="my_signature"):
        payload = {"alias": alias, "type": "sign"}
        return self._client.post("/keystore/create", payload)

    def create_encrypt(self, alias="my_encrypt"):
        """需要环境变量 RUM_KSPASSWD"""
        payload = {"alias": alias, "type": "encrypt"}
        return self._client.post("/keystore/create", payload)

    def get_keys(self):
        return self._client.get("/keystore/listall")

    def unbind_alias(self, alias):
        payload = {"alias": alias}
        return self._client.post("/keystore/remove", payload)

    def rebind_alias(self, alias, keyname, type_str):
        payload = {"alias": alias, "keyname": keyname, "type": type_str}
        return self._client.post("/keystore/bindalias", payload)

    def join_group(self, seed, sign_alias, encrypt_alias, urls):
        payload = {
            "seed": seed,
            "sign_alias": sign_alias,
            "encrypt_alias": encrypt_alias,
            "urls": urls,
        }
        return self._client.post("/group/join", payload)

    def list_groups(self):
        return self._client.get("/group/listall")

    def list_group(self, group_id):
        return self._client.get("/group/list", {"group_id": group_id})

    def group_info(self, group_id):
        return self._client.get(f"/group/{group_id}/info")

    def seed(self, group_id):
        return self._client.get(f"/group/seed", {"group_id": group_id})

    def trx(self, group_id, trx_id):
        return self._client.get(f"/trx/{group_id}/{trx_id}")

    def block(self, group_id, block_id):
        return self._client.get(f"/block/{group_id}/{block_id}")

    def producers(self, group_id):
        return self._client.get(f"/group/{group_id}/producers")

    def keylist(self, group_id):
        return self._client.get(f"/group/{group_id}/appconfig/keylist")

    def key(self, group_id, key):
        return self._client.get(f"/group/{group_id}/appconfig/{key}")

    def content(
        self,
        group_id: str,
        reverse: bool = False,
        start_trx: str = None,
        num: int = 20,
        include_start_trx: bool = False,
    ) -> List:

        payload = {
            "group_id": group_id,
            "num": num,
            "start_trx": json.dumps(start_trx),
            "reverse": json.dumps(reverse),
            "include_start_trx": json.dumps(include_start_trx),
        }

        return self._client.post(f"/group/getctn", payload)

    def _send(self, group_id: str, obj=None, sendtype=None, **kwargs) -> Dict:
        payload = NewTrx(group_id=group_id, obj=obj, sendtype=sendtype, **kwargs).__dict__
        return self._client.post("/group/content", payload)

    def like(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id=group_id, trx_id=trx_id, sendtype="Like")

    def dislike(self, group_id: str, trx_id: str) -> Dict:
        return self._send(group_id=group_id, trx_id=trx_id, sendtype="Dislike")

    def send_note(self, group_id: str, **kwargs):
        return self._send(group_id, sendtype="Add", objtype="Note", **kwargs)

    def reply(self, group_id: str, content: str, trx_id: str, images=None):
        return self.send_note(group_id, content=content, images=images, inreplyto=trx_id)

    def send_text(self, group_id: str, content: str, name: str = None):
        return self.send_note(group_id, content=content, name=name)

    def send_img(self, group_id: str, images):
        if type(images) != list:
            images = [images]
        return self.send_note(group_id, images=images)
