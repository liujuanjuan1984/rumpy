import logging
import os
from typing import Any, Dict, List

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import rumpy.utils as utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger(__name__)


class HttpRequest:
    def __init__(
        self,
        api_base: str = None,
        crtfile: str = None,
        jwt_token: str = None,
    ):

        requests.adapters.DEFAULT_RETRIES = 5
        self.api_base = api_base
        self._session = requests.Session()
        self._session.verify = utils.check_crtfile(crtfile)
        self._session.keep_alive = False
        self._session.headers.update(
            {
                "USER-AGENT": "rumpy.api",
                "Content-Type": "application/json",
            }
        )
        if jwt_token:
            self._session.headers.update({"Authorization": f"Bearer {jwt_token}"})
        if "127.0.0.1" in self.api_base:
            os.environ["NO_PROXY"] = ",".join([os.getenv("NO_PROXY", ""), self.api_base])

    def _request(self, method: str, endpoint: str, payload: Dict = {}, api_base=None):
        api_base = api_base or self.api_base or ""
        url = api_base + endpoint
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

    def get(self, endpoint: str, payload: Dict = {}, api_base=None):
        return self._request("get", endpoint, payload, api_base)

    def post(self, endpoint: str, payload: Dict = {}, api_base=None):
        return self._request("post", endpoint, payload, api_base)
