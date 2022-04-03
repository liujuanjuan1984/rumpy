from rumpy.client.api.base import BaseAPI


class PaidGroup(BaseAPI):
    def dapp(self):
        """Get Info of Paidgroup DApp"""
        resp = self._get("https://prs-bp2.press.one/api/dapps/PaidGroupMvm")
        if resp.get("success"):
            return resp.get("data")
        return resp

    def paidgroup(self):
        """Get Detail of a Paidgroup"""
        self._check_group_id()
        resp = self._get(f"https://prs-bp2.press.one/api/mvm/paidgroup/{self.group_id}")
        if resp.get("success"):
            return resp.get("data").get("group")
        return resp

    def payment(self):
        """Check Payment"""
        self._check_group_id()
        resp = self._get(
            f"https://prs-bp2.press.one/api/mvm/paidgroup/{self.group_id}/{self.group.eth_addr}"
        )
        if resp.get("success"):
            return resp.get("data").get("payment")
        return resp

    def announce(self, amount, duration):
        """Announce a Paidgroup"""
        self._check_group_id()
        self._check_owner()

        relay = {
            "group": self.group_id,
            "owner": self.group.eth_addr,
            "amount": str(amount),
            "duration": duration,
        }
        resp = self._post("https://prs-bp2.press.one/api/mvm/paidgroup/announce", relay)
        if resp.get("success"):
            return resp.get("data")
        return resp

    def pay(self):
        """Pay for a Paidgroup"""
        self._check_group_id()

        relay = {
            "user": self.group.eth_addr,
            "group": self.group_id,
        }
        resp = self._post("https://prs-bp2.press.one/api/mvm/paidgroup/pay", relay)
        if resp.get("success"):
            return resp.get("data")
        return resp
