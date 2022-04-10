import logging
import inspect
import requests
import urllib3

urllib3.disable_warnings()
from rumpy.client import api
from rumpy.client.api.base import BaseAPI
from rumpy.client.module import *
from rumpy.client.module_op import BaseDB

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

    def __init__(self,
                 port: int,
                 crtfile: str,
                 host: str = "127.0.0.1",
                 appid: str = "peer",
                 jwt_token: str = None,
                 usedb: bool = False,
                 dbname: str = "test_db",
                 dbecho: bool = False,
                 dbreset: bool = False):
        """
        port: 端口号
        crtfile: Rum 证书文件 server.crt 的绝对路径
        host: IP地址, 本地 "127.0.0.1" (默认), 服务器为公网 IP
        appid: 节点名，默认 "peer"
        jwt_token: 远程登录身份验证 token
        usedb: bool = False
        dbname: str = "test_db"
        dbecho: bool = False
        dbreset: bool = False
        """
        requests.adapters.DEFAULT_RETRIES = 5
        self.appid = appid
        self._session = requests.Session()
        self._session.verify = crtfile
        self._session.keep_alive = False

        self._session.headers.update({
            "USER-AGENT": "python.api",
            "Content-Type": "application/json",
        })
        if jwt_token:
            self._session.headers.update(
                {"Authorization": f"Bearer {jwt_token}"})
        self.baseurl = f"https://{host}:{port}/api/v1"
        self.usedb = usedb
        if self.usedb:
            self.db = BaseDB(dbname, echo=dbecho, reset=dbreset)

    def _request(self, method, url, relay={}):
        try:
            resp = self._session.request(method=method, url=url, json=relay)
            return resp.json()
        except Exception as e:  # SSLCertVerificationError
            resp = self._session.request(method=method,
                                         url=url,
                                         json=relay,
                                         verify=False)
            return resp.json()

    def get(self, url, relay={}):
        return self._request("get", url, relay)

    def post(self, url, relay={}):
        if self.usedb:
            resp = self._request("post", url, relay)
            if "trx_id" in resp:
                action = {
                    "group_id": self.group_id,
                    "trx_id": resp["trx_id"],
                    "func": "post",
                    "params": {
                        "url": url,
                        "relay": relay
                    },
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
