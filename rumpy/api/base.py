import logging
from typing import Any, Dict, List

from rumpy.client._requests import HttpRequest

logger = logging.getLogger(__name__)


class BaseAPI:
    def __init__(self, http: HttpRequest = None):
        self._http = http

    def _get(self, endpoint: str, payload: Dict = {}):
        api_base = None
        if hasattr(self, "API_BASE"):
            api_base = self.API_BASE
        return self._http.get(endpoint, payload, api_base)

    def _post(self, endpoint: str, payload: Dict = {}):
        api_base = None
        if hasattr(self, "API_BASE"):
            api_base = self.API_BASE
        return self._http.post(endpoint, payload, api_base)

    def check_group_id_as_required(self, group_id=None):
        group_id = group_id or self._http.group_id
        if not group_id:
            raise ValueError("group_id is required, now it's None.")
        return group_id

    def check_group_joined_as_required(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        if group_id not in self._http.api.groups_id:
            raise ValueError(f"You are not in this group: <{group_id}>.")
        return group_id

    def check_group_owner_as_required(self, group_id=None):
        group_id = self.check_group_joined_as_required(group_id)
        info = self._http.api.group_info(group_id)
        if info.user_pubkey != info.owner_pubkey:
            raise ValueError(f"You are not the owner of this group: <{group_id}>.")
        return group_id

    def is_joined(self, group_id=None) -> bool:
        try:
            self.check_group_joined_as_required(group_id)
            return True
        except:
            return False

    def is_owner(self, group_id=None) -> bool:
        """return True if I create this group else False"""
        try:
            self.check_group_owner_as_required(group_id)
            return True
        except:
            return False

    def raise_error(self, resp, except_err=None):
        if err := resp.get("error"):
            if err != except_err:
                raise ValueError(err)
        return resp
