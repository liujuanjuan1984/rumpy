from typing import Any, Dict, List

from rumpy.client._requests import HttpRequest


class BaseAPI:
    def __init__(self, http: HttpRequest = None):
        self._http = http

    def _get(self, endpoint: str, payload: Dict = {}, api_base=None):
        if hasattr(self, "API_BASE"):
            api_base = api_base or self.API_BASE
        return self._http.get(endpoint, payload, api_base)

    def _post(self, endpoint: str, payload: Dict = {}, api_base=None):
        if hasattr(self, "API_BASE"):
            api_base = api_base or self.API_BASE
        return self._http.post(endpoint, payload, api_base)

    @property
    def group_id(self):
        return self._http.group_id

    def check_group_id_as_required(self):
        if self.group_id == None:
            raise ValueError("group_id is required, now it's None.")

    def check_group_joined_as_required(self):
        self.check_group_id_as_required()
        if self.group_id not in self._http.node.groups_id:
            raise ValueError(f"You are not in this group: <{self.group_id}>.")

    def check_group_owner_as_required(self):
        self.check_group_id_as_required()
        self.check_group_joined_as_required()
        if self._http.group.pubkey != self._http.group.owner:
            raise ValueError(f"You are not the owner of this group: <{self.group_id}>.")
