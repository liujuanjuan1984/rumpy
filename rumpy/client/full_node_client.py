import logging
import os

from rumpy.api import BaseAPI, FullNodeAPI, PaidGroup
from rumpy.client._flask_extensions import _init_app
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS

logger = logging.getLogger(__name__)


class FullNode:
    _group_id = None

    def __init__(
        self,
        protocol=None,
        port=None,
        host="127.0.0.1",
        crtfile=None,
        api_base=None,
        jwt_token=None,
    ):
        if api_base is None:
            if port is None:
                port = os.getenv("RUM_PORT", 51194)
            if crtfile is None:
                local_crtfile = r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum-bin\certs\server.crt"
                crtfile = os.getenv("RUM_CRTFILE", local_crtfile)
            if protocol is None:
                if host in ["127.0.0.1", "localhost"]:
                    protocol = "http"
                else:
                    protocol = "https"
            api_base = ApiBaseURLS(protocol=protocol, port=port, host=host).FULL_NODE

        self.http = HttpRequest(api_base=api_base, crtfile=crtfile, jwt_token=jwt_token)
        self.api = self.http.api = FullNodeAPI(self.http)
        self.paid = self.http.paid = PaidGroup(self.http)
        # TODO:paid其实也是 api 的一类，这个处理需要集中搞下

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
        self.http.group_id = group_id

    def init_app(self, app, rum_kspasswd=None, rum_port=None):
        return _init_app(self, app, rum_kspasswd, rum_port)
