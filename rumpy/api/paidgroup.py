import logging

from rumpy.api.base import BaseAPI

logger = logging.getLogger(__name__)


class PaidGroup(BaseAPI):
    def dapp(self):
        """Get Info of Paidgroup DApp"""
        resp = self._client.get("/dapps/PaidGroupMvm", api_base=self._client.api_base_paid)
        if resp.get("success"):
            return resp.get("data")
        return resp

    def paidgroup(self):
        """Get Detail of a Paidgroup"""
        self.check_group_id_required()
        resp = self._client.get(
            f"/mvm/paidgroup/{self._client.group_id}",
            api_base=self._client.api_base_paid,
        )
        if resp.get("success"):
            return resp.get("data").get("group")
        return resp

    def payment(self):
        """Check Payment"""
        self.check_group_id_required()
        resp = self._client.get(
            f"/mvm/paidgroup/{self._client.group_id}/{self._client.group.eth_addr}",
            api_base=self._client.api_base_paid,
        )
        if resp.get("success"):
            return resp.get("data").get("payment")
        return resp

    def announce(self, amount, duration):
        """Announce a Paidgroup"""
        self.check_group_id_required()
        self.check_owner_required()

        payload = {
            "group": self._client.group_id,
            "owner": self._client.group.eth_addr,
            "amount": str(amount),
            "duration": duration,
        }
        resp = self._client.post(
            "/mvm/paidgroup/announce",
            payload,
            api_base=self._client.api_base_paid,
        )
        if resp.get("success"):
            return resp.get("data")
        return resp

    def pay(self):
        """Pay for a Paidgroup"""
        self.check_group_id_required()

        payload = {
            "user": self._client.group.eth_addr,
            "group": self._client.group_id,
        }
        resp = self._client.post("/mvm/paidgroup/pay", payload, api_base=self._client.api_base_paid)
        if resp.get("success"):
            return resp.get("data")
        return resp
