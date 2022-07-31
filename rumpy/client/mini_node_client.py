import logging
import time

from rumpy.client._requests import HttpRequest

logger = logging.getLogger(__name__)

import base64
from typing import Any, Dict, List
from urllib import parse

import rumpy.utils as utils
from rumpy.exceptions import *
from rumpy.types.sign_trx import trx_decrypt, trx_encrypt
from rumpy.types.data import *
from rumpy.types.pack_trx import *


class MiniNode:
    """TODO: add more methods
    r.POST("/v1/node/groupctn/:group_id", h.GetContentNSdk)
        r.POST("/v1/node/getchaindata/:group_id", h.GetDataNSdk)
    """

    def __init__(self, seedurl: str):

        info = utils.decode_seed_url(seedurl)
        url = parse.urlparse(info["url"])
        if not info["url"]:
            raise ParamValueError("Invalid seed url. param u is required.eg:  u=http://127.0.0.1:51234?jwt=xxx")
        jwt = parse.parse_qs(url.query)
        if jwt:
            jwt = ["jwt"][0]
        else:
            jwt = None
        api_base = f"{url.scheme}://{url.netloc}/api/v1/node"

        self.group_id = info["group_id"]
        self.aes_key = bytes.fromhex(info["chiperkey"])
        self.http = HttpRequest(api_base=api_base, jwt_token=jwt)

    def send_note(
        self,
        private_key,
        content: str = None,
        name: str = None,
        images: List = None,
        edit_trx_id: str = None,
        del_trx_id: str = None,
        reply_trx_id: str = None,  # inreplyto,
        timestamp=None,
        seedurl=None,
    ):
        obj = Mini.pack_note_obj(content, name, images, edit_trx_id, del_trx_id, reply_trx_id)
        return self.send_trx(private_key, obj, timestamp, seedurl)

    def like(self, private_key, trx_id, like_type="Like", timestamp=None, seedurl=None):
        obj = Mini.pack_like_obj(trx_id, like_type)
        return self.send_trx(private_key, obj, timestamp, seedurl)

    def send_trx(self, private_key, obj, timestamp=None, seedurl=None):
        """
        obj: dict,packed from rumpy.types.pack_trx
        timestamp:2022-10-05 12:34
        """
        if seedurl:
            self.__init__(seedurl)
        if isinstance(private_key, str):
            private_key = bytes.fromhex(private_key)
        # 此处开放了时间戳的自定义
        if timestamp and isinstance(timestamp, str):
            timestamp = timestamp.replace("/", "-")[:16]
            timestamp = time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M"))
        trx = trx_encrypt(self.group_id, self.aes_key, private_key, obj, timestamp)
        resp = self.http.post(endpoint=f"/trx/{self.group_id}", payload=trx)
        return resp

    def encrypt_trx(self, encrypted_trx: dict):
        return trx_decrypt(self.aes_key, encrypted_trx)
