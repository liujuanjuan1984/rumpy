from rumpy.api import Group, Node, PaidGroup
from rumpy.api.light_api import LightAPI
from rumpy.client._requests import HttpRequest


class LightNode:
    def __init__(self, port, api_base: str = None, crtfile=None):
        api_base = api_base or f"https://127.0.0.1:{port}/nodesdk_api/v1"
        self.http = _requests.HttpRequest(api_base)
        self.api = LightAPI(self.http)


class FullNode:
    _group_id = None

    def __init__(self, port, crtfile=None, api_base: str = None):
        api_base = api_base or f"https://127.0.0.1:{port}/api/v1"
        self.http = _requests.HttpRequest(api_base)
        self.http.api_base_app = f"https://127.0.0.1:{port}/app/api/v1"
        self.http.api_base_paid = "https://prs-bp2.press.one/api"
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
