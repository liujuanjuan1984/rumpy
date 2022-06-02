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

    def paidgroup(self):
        """Get Detail of a Paidgroup"""
        self.check_group_id_as_required()
        resp = self._get(f"/mvm/paidgroup/{self.group_id}")
        if resp.get("success"):
            return resp.get("data").get("group")
        return resp

    def payment(self):
        """Check Payment"""
        self.check_group_id_as_required()
        resp = self._get(f"/mvm/paidgroup/{self.group_id}/{self._http.group.eth_addr}")
        if resp.get("success"):
            return resp.get("data").get("payment")
        return resp

    def announce(self, amount, duration):
        """Announce a Paidgroup"""
        self.check_group_id_as_required()
        self.check_group_owner_as_required()

        payload = {
            "group": self.group_id,
            "owner": self._http.group.eth_addr,
            "amount": str(amount),
            "duration": duration,
        }
        resp = self._post("/mvm/paidgroup/announce", payload)
        if resp.get("success"):
            return resp.get("data")
        return resp

    def pay(self):
        """Pay for a Paidgroup"""
        self.check_group_id_as_required()

        payload = {
            "user": self._http.group.eth_addr,
            "group": self.group_id,
        }
        resp = self._post("/mvm/paidgroup/pay", payload)
        if resp.get("success"):
            return resp.get("data")
        return resp
