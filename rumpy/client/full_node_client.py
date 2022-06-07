import logging

from rumpy.api import BaseAPI, FullNodeAPI, PaidGroup
from rumpy.client._flask_extensions import _init_app
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS

logger = logging.getLogger(__name__)


class FullNode:
    _group_id = None

    def __init__(self, port, host="127.0.0.1", crtfile=None):
        _apis = ApiBaseURLS(port=port, host=host)
        self.http = HttpRequest(_apis.FULL_NODE)
        self.api = self.http.api = FullNodeAPI(self.http)
        self.paid = self.http.paid = PaidGroup(self.http)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
        self.http.group_id = group_id

    def init_app(self, app, rum_kspasswd=123456, rum_port=62663):
        return _init_app(self, app, rum_kspasswd, rum_port)
