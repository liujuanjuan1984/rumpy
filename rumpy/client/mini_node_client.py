import logging
import time

logger = logging.getLogger(__name__)

from typing import Any, Dict, List
from urllib import parse

from eth_account import Account
from eth_utils.hexadecimal import encode_hex

import rumpy.utils as utils
from rumpy.client import HttpRequest
from rumpy.exceptions import *
from rumpy.types.data import *
from rumpy.types.pack_trx import *
from rumpy.types.sign_trx import get_content_param, trx_decrypt, trx_encrypt


class MiniNode:
    # TODO: r.POST("/v1/node/getchaindata/:group_id", h.GetDataNSdk)

    def __init__(self, seedurl: str):

        info = utils.decode_seed_url(seedurl)
        url = parse.urlparse(info["url"])
        if not info["url"]:
            raise ParamValueError("Invalid seed url. param u is required.eg:  u=http://127.0.0.1:51234?jwt=xxx")
        jwt = parse.parse_qs(url.query)
        if jwt:
            jwt = jwt["jwt"][0]
        else:
            jwt = None

        self.http = HttpRequest(
            api_base=f"{url.scheme}://{url.netloc}/api/v1", jwt_token=jwt, is_session=False, is_connection=False
        )
        self.group_id = info["group_id"]
        self.aes_key = bytes.fromhex(info["chiperkey"])

    @staticmethod
    def create_private_key() -> str:
        acc = Account.create()
        private_key = encode_hex(acc.privateKey)
        return private_key

    @staticmethod
    def private_key_to_address(private_key) -> str:
        return Account.from_key(private_key).address

    @staticmethod
    def check_private_key(private_key: str) -> bytes:
        if isinstance(private_key, int):
            private_key = hex(private_key)
        if isinstance(private_key, str):
            if private_key.startswith("0x"):
                private_key = bytes.fromhex(private_key[2:])
            else:
                private_key = bytes.fromhex(private_key)
        elif isinstance(private_key, bytes):
            pass
        else:
            raise ParamValueError(
                "Invalid private key. param private_key is required.eg:  private_key=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            )
        if len(private_key) != 32:
            raise ParamValueError("Invalid private key. param private_key is required.eg:  private_key=xxx")
        return private_key

    @staticmethod
    def private_key_to_keystore(private_key, password: str):
        return Account.from_key(private_key).encrypt(password=password)

    @staticmethod
    def keystore_to_private_key(keystore: Dict, password: str) -> str:
        pvtkey = Account.decrypt(keystore, password)
        private_key = encode_hex(pvtkey)
        return private_key

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
        return self.send_trx(private_key, obj=obj, timestamp=timestamp, seedurl=seedurl)

    def like(self, private_key, trx_id, like_type="Like", timestamp=None, seedurl=None):
        obj = Mini.pack_like_obj(trx_id, like_type)
        return self.send_trx(private_key, obj=obj, timestamp=timestamp, seedurl=seedurl)

    def update_profile(self, private_key, name=None, image=None, timestamp=None, seedurl=None):
        if name is None and image is None:
            raise ParamValueError("Invalid profile. param name or image is required.eg:  name=xxx or image=xxx")
        person = Mini.pack_person_obj(name=name, image=image)
        return self.send_trx(private_key, person=person, timestamp=timestamp, seedurl=seedurl)

    def send_trx(self, private_key, obj=None, person=None, timestamp=None, seedurl=None):
        """
        obj: dict,packed from rumpy.types.pack_trx
        timestamp:2022-10-05 12:34
        """
        if seedurl:
            self.__init__(seedurl)
        private_key = self.check_private_key(private_key)
        # 此处开放了时间戳的自定义
        if timestamp and isinstance(timestamp, str):
            timestamp = timestamp.replace("/", "-")[:16]
            timestamp = time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M"))
        trx = trx_encrypt(self.group_id, self.aes_key, private_key, obj=obj, person=person, timestamp=timestamp)
        return self.http.post(endpoint=f"/node/trx/{self.group_id}", payload=trx)

    def get_trx(self, trx_id):
        return self.http.get(endpoint=f"/trx/{self.group_id}/{trx_id}")

    def encrypt_trx(self, encrypted_trx: dict):
        return trx_decrypt(self.aes_key, encrypted_trx)

    def trx(self, trx_id):
        encrypted_trx = self.get_trx(trx_id)
        return self.encrypt_trx(encrypted_trx)

    def get_content(
        self,
        start_trx: str = None,
        num: int = 20,
        reverse: bool = False,
        include_start_trx: bool = False,
        senders=None,
        trx_types=None,
    ):
        payload = get_content_param(self.aes_key, self.group_id, start_trx, num, reverse, include_start_trx, senders)
        encypted_trxs = self.http.post(f"/node/groupctn/{self.group_id}", payload=payload)
        try:
            trxs = [self.encrypt_trx(i) for i in encypted_trxs]
            if trx_types:
                return [trx for trx in trxs if (utils.trx_type(trx) in trx_types)]
            else:
                return trxs
        except Exception as e:
            logger.warning(f"get_content error: {e}")
            return encypted_trxs

    def get_all_contents(self, senders=None, trx_types=None):
        """获取所有内容trxs的生成器，可以用 for...in...来迭代。"""
        trx_id = None
        trxs = self.get_content(start_trx=trx_id, num=200, senders=senders, trx_types=trx_types)
        checked_trxids = []
        trx_types = trx_types or []
        senders = senders or []
        while trxs:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            for trx in trxs:
                flag1 = (utils.trx_type(trx) in trx_types) or (not trx_types)
                flag2 = (trx.get("Publisher", "") in senders) or (not senders)
                if flag1 and flag2:
                    yield trx
            trx_id = utils.get_last_trxid_by_chain(trx_id, trxs, reverse=False)
            trxs = self.get_content(start_trx=trx_id, num=200, senders=senders, trx_types=trx_types)
