import os
import logging
import inspect
import requests
from typing import Dict, List, Any
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from rumpy.client import api
from rumpy.client.api.base import BaseAPI
from rumpy.client.module import *
from rumpy.client.module_op import BaseDB
from rumpy.client.config import PORT, CRTFILE

logger = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseAPI)


class RumClient:
    _group_id = None
    group = api.Group()
    node = api.Node()
    config = api.GroupConfig()
    paid = api.PaidGroup()
    db = None

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
        usedb: bool = False,
        dbname: str = "test_db",
        dbecho: bool = False,
        dbreset: bool = False,
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
            "usedb": usedb,
            "dbname": dbname,
            "dbecho": dbecho,
            "dbreset": dbreset,
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
        self.baseurl = f"https://{host}:{port}/api/v1"
        self.baseurl_app = f"https://{host}:{port}/app/api/v1"
        os.environ["NO_PROXY"] = ",".join([os.getenv("NO_PROXY", ""), self.baseurl, self.baseurl_app])

        self.usedb = usedb
        if self.usedb:
            self.db = BaseDB(
                dbname,
                echo=dbecho,
                reset=dbreset,
            )

    def _request(self, method: str, url: str, relay: Dict = {}):

        try:
            resp = self._session.request(method=method, url=url, json=relay)
        except Exception as e:  # SSLCertVerificationError
            resp = self._session.request(method=method, url=url, json=relay, verify=False)
        print(resp.status_code, url)
        return resp.json()

    def get(self, url: str, relay: Dict = {}):
        return self._request("get", url, relay)

    def post(self, url: str, relay: Dict = {}):
        if self.usedb:
            resp = self._request("post", url, relay)
            if "trx_id" in resp:
                action = {
                    "group_id": self.group_id,
                    "trx_id": resp["trx_id"],
                    "func": "post",
                    "params": {"url": url, "relay": relay},
                }
                self.db.save(Action(action))
            return resp
        else:
            return self._request("post", url, relay)

    @property
    def group_id(self):
        logger.info(f"group_id:{self._group_id}")
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
