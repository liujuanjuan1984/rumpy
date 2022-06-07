import logging

from rumpy.api.base import BaseAPI
from rumpy.types.data import API_PAYMENT_GATEWAY

logger = logging.getLogger(__name__)


class PaidGroup(BaseAPI):
    API_BASE = API_PAYMENT_GATEWAY

    def dapp(self):
        """Get Info of Paidgroup DApp"""
        resp = self._get("/dapps/PaidGroupMvm")
        if resp.get("success"):
            return resp.get("data")
        return resp

    def paidgroup(self, group_id=None):
        """Get Detail of a Paidgroup"""
        group_id = self.check_group_id_as_required(group_id)
        resp = self._get(f"/mvm/paidgroup/{group_id}")
        if resp.get("success"):
            return resp.get("data").get("group")
        return resp

    def payment(self, group_id=None):
        """Check Payment"""
        group_id = self.check_group_id_as_required(group_id)
        resp = self._get(f"/mvm/paidgroup/{group_id}/{self._http.api.eth_addr}")
        if resp.get("success"):
            return resp.get("data").get("payment")
        return resp

    def announce(self, amount, duration, group_id=None):
        """Announce a Paidgroup"""
        group_id = self.check_group_owner_as_required(group_id)

        payload = {
            "group": group_id,
            "owner": self._http.api.eth_addr,
            "amount": str(amount),
            "duration": duration,
        }
        resp = self._post("/mvm/paidgroup/announce", payload)
        if resp.get("success"):
            return resp.get("data")
        return resp

    def pay(self, group_id=None):
        """Pay for a Paidgroup"""
        group_id = self.check_group_id_as_required(group_id)

        payload = {
            "user": self._http.api.eth_addr,
            "group": group_id,
        }
        resp = self._post("/mvm/paidgroup/pay", payload)
        if resp.get("success"):
            return resp.get("data")
        return resp
