import logging
import os
from typing import Any, Dict, List

import requests

import rumpy.utils as utils
from rumpy.exceptions import *

logger = logging.getLogger(__name__)


class HttpRequest:
    def __init__(
        self,
        api_base: str = None,
        crtfile: str = None,
        jwt_token: str = None,
        is_session: bool = True,
        is_connection: bool = False,
        no_proxy: bool = True,
    ):

        requests.adapters.DEFAULT_RETRIES = 5
        self.api_base = api_base or "http://127.0.0.1"
        if is_session:
            self._session = requests.Session()
        else:
            self._session = requests

        self._session.verify = utils.check_crtfile(crtfile)
        self._session.keep_alive = self.is_connection = is_connection

        self.headers = {
            "USER-AGENT": "rumpy.api",
            "Content-Type": "application/json",
        }
        if jwt_token:
            self.headers.update({"Authorization": f"Bearer {jwt_token}"})
        if not is_connection:
            self.headers.update({"Connection": "close"})

        flag = ("127.0.0.1" in self.api_base and self.api_base not in _no_proxy) or no_proxy
        if flag:
            os.environ["NO_PROXY"] = ",".join([os.getenv("NO_PROXY", ""), self.api_base])

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: Dict = {},
        api_base=None,
        url=None,
    ):
        if not url:
            api_base = api_base or self.api_base
            if not api_base:
                raise ParamValueError(f"api_base is null, {api_base}")
            url = utils.get_url(api_base, endpoint)

        try:
            resp = self._session.request(method=method, url=url, json=payload, headers=self.headers)
        except Exception as e:  # SSLCertVerificationError
            logger.warning(f"Exception {e}")
            resp = self._session.request(
                method=method, url=url, json=payload, verify=False, headers=self.headers
            )

        try:
            resp_json = resp.json()
        except Exception as e:
            logger.warning(f"Exception {e}")
            resp_json = {}

        if resp.status_code != 200:
            logger.info(f"payload:{payload}")
            logger.info(f"url:{url}")
            logger.info(f"resp_json:{resp_json}")
            logger.info(f"resp.status_code:{resp.status_code}")

        logger.debug(f"payload:{payload}")
        logger.debug(f"url:{url}")
        logger.debug(f"resp_json:{resp_json}")
        logger.debug(f"resp.status_code:{resp.status_code}")

        return resp_json

    def get(self, endpoint: str, payload: Dict = {}, api_base=None, url=None):
        return self._request("get", endpoint, payload, api_base, url)

    def post(self, endpoint: str, payload: Dict = {}, api_base=None, url=None):
        return self._request("post", endpoint, payload, api_base, url)
