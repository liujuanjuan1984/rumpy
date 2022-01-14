# -*- coding: utf-8 -*-

import inspect
import requests
from rumpy.client import api
from rumpy.client.api.base import BaseRumAPI
from rumpy.client.data import ClientParams

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
        self.appid = cp.appid
        self._session = requests.Session()
        self._session.verify = cp.crtfile
        self._session.headers.update(
            {
                "USER-AGENT": "python.api",
                "Content-Type": "application/json",
            }
        )

        self.baseurl = f"https://{cp.host}:{cp.port}/api/v1"

    def _request(self, method, url, **kwargs):
        resp = self._session.request(method=method, url=url, **kwargs)
        return resp.json()

    def get(self, url):
        return self._request("get", url)

    def post(self, url, data):
        return self._request("post", url, json=data)
