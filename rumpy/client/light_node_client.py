import logging
import os

from rumpy.api import LightNodeAPI, PaidGroup
from rumpy.client._flask_extensions import _init_app
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS

logger = logging.getLogger(__name__)


class LightNode:
    def __init__(self, port=None, host="127.0.0.1", crtfile=None):
        if port is None:
            port = os.getenv("RUM_PORT", 6002)
        api_base = ApiBaseURLS(port=port, host=host).LIGHT_NODE
        self.http = HttpRequest(api_base)
        self.api = LightNodeAPI(self.http)

    def init_app(self, app, rum_kspasswd=None, rum_port=None):
        return _init_app(self, app, rum_kspasswd, rum_port)
