# -*- coding: utf-8 -*-

import datetime
from dataclasses import dataclass
import inspect
import requests
import urllib3

urllib3.disable_warnings()
from . import api
from .api.base import BaseRumAPI


@dataclass
class ClientParams:
    """
    :param appid, str, Rum 客户端标识，自定义，随便写
    :param port, int, Rum 服务 端口号
    :param host,str, Rum 服务 host，通常是 127.0.0.1
    :param crtfile, str, Rum 的 server.crt 文件的绝对路径

    {
        "port":8002,
        "host":"127.0.0.1",
        "appid":"peer"
        "crtfile":"",
    }
    """

    port: int
    crtfile: str
    host: str = "127.0.0.1"
    appid: str = "peer"
    jwt_token: str = None


def _is_api_endpoint(obj):
    return isinstance(obj, BaseRumAPI)


class RumClient:

    group = api.RumGroup()
    node = api.RumNode()
    trx = api.RumTrx()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, **kwargs):
        cp = ClientParams(**kwargs)
        requests.adapters.DEFAULT_RETRIES = 5
        self.appid = cp.appid
        self._session = requests.Session()
        self._session.verify = cp.crtfile
        self._session.keep_alive = False

        self._session.headers.update(
            {
                "USER-AGENT": "python.api",
                "Content-Type": "application/json",
            }
        )
        if cp.jwt_token:
            self._session.headers.update({"Authorization": f"Bearer {cp.jwt_token}"})
        self.baseurl = f"https://{cp.host}:{cp.port}/api/v1"

    def _request(self, method, url, relay={}):
        resp = self._session.request(method=method, url=url, json=relay)
        return resp.json()

    def get(self, url, relay={}):
        return self._request("get", url, relay)

    def post(self, url, relay={}):
        return self._request("post", url, relay)

    def ts2datetime(self, ts):
        # 把 rum 中的时间戳（纳米级）转换一下
        return datetime.datetime.fromtimestamp(int(int(ts) / 1000000000))
