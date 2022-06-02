from rumpy.api import Group, Node, PaidGroup
from rumpy.api.light_node import LightNodeAPI
from rumpy.client._requests import HttpRequest
from rumpy.types.data import ApiBaseURLS


class LightNode:
    def __init__(self, port, host="127.0.0.1", crtfile=None):

        api_base = ApiBaseURLS(port=port, host=host).LIGHT_NODE
        self.http = _requests.HttpRequest(api_base)
        self.api = LightNodeAPI(self.http)

    def init_app(self, app):
        return _init_app(self, app)


class FullNode:
    _group_id = None

    def __init__(self, port, host="127.0.0.1", crtfile=None):
        _apis = ApiBaseURLS(port=port, host=host)
        self.http = _requests.HttpRequest(_apis.FULL_NODE)
        self.http.api_base_app = _apis.FULL_NODE_APP
        self.http.group_id = self.group_id
        self.group = self.http.group = Group(self.http)
        self.node = self.http.node = Node(self.http)
        self.paid = self.http.paid = PaidGroup(self.http)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id
        self.http.group_id = group_id

    def init_app(self, app):
        return _init_app(self, app)


def _init_app(_client, flask_app):
    """for flask extensions"""
    if not hasattr(flask_app, "extensions"):
        flask_app.extensions = {}
    flask_app.extensions["rum"] = _client

    flask_app.config.setdefault("RUM_KSPASSWD", 123456)
    flask_app.config.setdefault("RUM_PORT", 6002)
    flask_app.rum = _client
    return flask_app
