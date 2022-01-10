# -*- coding: utf-8 -*-

from typing import List, Dict


class BaseRumAPI:
    def __init__(self, client=None):
        self._client = client

    def _get(self, url: str):
        return self._client.get(url)

    def _post(self, url: str, data=None):
        return self._client.post(url, data)

    @property
    def baseurl(self) -> str:
        return self._client.baseurl
