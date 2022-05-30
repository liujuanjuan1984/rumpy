from typing import Any, Dict, List


class BaseAPI:
    def __init__(self, client=None):
        self._client = client

    def _get(self, path: str, payload: Dict = {}, api_base=None):
        return self._client.get(path, payload, api_base)

    def _post(self, path: str, payload: Dict = {}, api_base=None):
        return self._client.post(path, payload, api_base)

    @property
    def group_id(self):
        return self._client.group_id

    def check_group_id_as_required(self):
        if self.group_id == None:
            raise ValueError("client.group_id is required, now it's None.")

    def check_group_joined_as_required(self):
        self.check_group_id_as_required()
        if self.group_id not in self._client.node.groups_id:
            raise ValueError(f"You are not in this group: <{self.group_id}>.")

    def check_group_owner_as_required(self):
        self.check_group_id_as_required()
        self.check_group_joined_as_required()
        if self._client.group.pubkey != self._client.group.owner:
            raise ValueError(f"You are not the owner of this group: <{self.group_id}>.")
