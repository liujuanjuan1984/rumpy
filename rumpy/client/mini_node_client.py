import logging
import time

from rumpy.client._requests import HttpRequest

logger = logging.getLogger(__name__)

from rumpy.types import TrxDecrypt, TrxEncrypt


class MiniNode:
    """TODO: add more methods
    r.POST("/v1/node/groupctn/:group_id", h.GetContentNSdk)
        r.POST("/v1/node/getchaindata/:group_id", h.GetDataNSdk)
    """

    def __init__(self, group_id: str, aes_key: str, apihost: str):
        self.group_id = group_id
        self.aes_key = bytes.fromhex(aes_key)
        self.apihost = apihost
        self.http = HttpRequest(api_base=f"{apihost}/api/v1/node")

    def send_trx(self, private_key: str, obj=None, timestamp=None, **kwargs):
        """
        timestamp:2022-10-05 12:34
        """

        if isinstance(private_key, str):
            private_key = bytes.fromhex(private_key)
        if timestamp and isinstance(timestamp, str):
            timestamp = time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M"))
        obj = obj or ContentObj(**kwargs).to_dict()
        trx = TrxEncrypt(self.group_id, self.aes_key, private_key, obj, timestamp)
        resp = self.http.post(endpoint=f"/trx/{self.group_id}", payload=trx)
        return resp

    def encrypt_trx(self, encrypted_trx: dict):
        return TrxDecrypt(self.aes_key, encrypted_trx)
