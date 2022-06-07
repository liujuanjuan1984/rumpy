import logging

from rumpy.api import LightNodeAPI, PaidGroup
from rumpy.client._flask_extensions import _init_app
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS

logger = logging.getLogger(__name__)


class LightNode:
    def __init__(self, port, host="127.0.0.1", crtfile=None):

        api_base = ApiBaseURLS(port=port, host=host).LIGHT_NODE
        self.http = HttpRequest(api_base)
        self.api = LightNodeAPI(self.http)

    def init_app(self, app, rum_kspasswd=123456, rum_port=6002):
        return _init_app(self, app, rum_kspasswd, rum_port)
