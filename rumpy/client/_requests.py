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

logger = logging.getLogger(__name__)


class HttpRequest:
    def __init__(
        self,
        api_base,
        port: int = None,
        crtfile: str = None,
        host: str = "127.0.0.1",
        appid: str = "peer",
        jwt_token: str = None,
    ):

        requests.adapters.DEFAULT_RETRIES = 5
        self.api_base = api_base
        self._session = requests.Session()
        self._session.verify = crtfile or False
        self._session.keep_alive = False
        self._session.headers.update(
            {
                "USER-AGENT": "rumpy.api",
                "Content-Type": "application/json",
            }
        )
        if jwt_token:
            self._session.headers.update({"Authorization": f"Bearer {jwt_token}"})
        os.environ["NO_PROXY"] = ",".join([os.getenv("NO_PROXY", ""), self.api_base])

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
