import logging
import os

from rumpy.api import LightNodeAPI, PaidGroup
from rumpy.client._flask_extensions import _init_app
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS

logger = logging.getLogger(__name__)


class LightNode:
    _group_id = None

    def __init__(self, protocol="http", port=None, host="127.0.0.1", crtfile=None):
        if port is None:
            port = os.getenv("RUM_PORT", 6002)
        if crtfile is None:
            local_crtfile = r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum-bin\certs\server.crt"
            crtfile = os.getenv("RUM_CRTFILE", local_crtfile)
        api_base = ApiBaseURLS(protocol=protocol, port=port, host=host).LIGHT_NODE
        self.http = HttpRequest(api_base=api_base, crtfile=crtfile)
        # TODO:某些请求，会检查 node 运行目录下的 server.crt 而不是传入的 文件。如何统一？
        self.api = self.http.api = LightNodeAPI(self.http)

    def init_app(self, app, rum_kspasswd=None, rum_port=None):
        return _init_app(self, app, rum_kspasswd, rum_port)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
        self.http.group_id = group_id
