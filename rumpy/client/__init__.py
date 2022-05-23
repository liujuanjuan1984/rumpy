import inspect
import logging
import os
import sys
from typing import Any, Dict, List

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from rumpy import api
from rumpy.api.base import BaseAPI
from rumpy.client.config import CRTFILE, PORT

logger = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseAPI)


class RumClient:
    _group_id = None
    group = api.Group()
    node = api.Node()
    config = api.GroupConfig()
    paid = api.PaidGroup()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(
        self,
        port: int = None,
        crtfile: str = None,
        host: str = "127.0.0.1",
        appid: str = "peer",
        jwt_token: str = None,
        api_base: str = None,
    ):
        """
        :param appid, str, Rum 客户端标识，自定义，随便写
        :param port, int, Rum 服务 端口号
        :param host,str, Rum 服务 host，通常是 127.0.0.1
        :param crtfile, str, Rum 的 server.crt 文件的绝对路径
        """
        port = port or PORT
        crtfile = crtfile or CRTFILE
        self.client_params = {
            "host": host,
            "port": port,
            "appid": appid,
            "crtfile": crtfile,
            "jwt_token": jwt_token,
        }
        requests.adapters.DEFAULT_RETRIES = 5

        self._session = requests.Session()
        self._session.verify = crtfile or False
        self._session.keep_alive = False
        self._session.headers.update(
            {
                "USER-AGENT": "python.api",
                "Content-Type": "application/json",
            }
        )
        if jwt_token:
            self._session.headers.update({"Authorization": f"Bearer {jwt_token}"})
        self.api_base = f"https://{host}:{port}/api/v1"
        self.api_base_app = f"https://{host}:{port}/app/api/v1"
        self.api_base_paid = "https://prs-bp2.press.one/api"
        os.environ["NO_PROXY"] = ",".join([os.getenv("NO_PROXY", ""), self.api_base, self.api_base_app])

    def _request(self, method: str, path: str, payload: Dict = {}, api_base=None):
        url = (api_base or self.api_base) + path
        try:
            resp = self._session.request(method=method, url=url, json=payload)
        except Exception as e:  # SSLCertVerificationError
            logger.warning(f"Exception {e}")
            resp = self._session.request(method=method, url=url, json=payload, verify=False)

        try:
            body_json = resp.json()
        except Exception as e:
            logger.warning(f"Exception {e}")
            body_json = {}

        if resp.status_code != 200:
            logger.warning(f"{resp.status_code}, {resp.json()}")
        return body_json

    def get(self, path: str, payload: Dict = {}, api_base=None):
        return self._request("get", path, payload, api_base)

    def post(self, path: str, payload: Dict = {}, api_base=None):
        return self._request("post", path, payload, api_base)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
