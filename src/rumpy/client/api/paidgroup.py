from rumpy.client.api.base import BaseAPI


class PaidGroup(BaseAPI):
    def dapp(self):
        """Get Info of Paidgroup DApp"""
        resp = self._get("https://prs-bp2.press.one/api/mvm/paidgroup")
        return resp.get("data")

    def paidgroup(self):
        """Get Detail of a Paidgroup"""
        self._check_group_id()
        resp = self._get(f"https://prs-bp2.press.one/api/mvm/paidgroup/{self.group_id}")

        return resp.get("data").get("group")

    def payment(self):
        """Check Payment"""
        self._check_group_id()
        resp = self._get(
            f"https://prs-bp2.press.one/api/mvm/paidgroup/{self.group_id}/{self.group.eth_addr}"
        )
        return resp.get("data").get("payment")

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
        return resp.get("data")

    def pay(self):
        """Pay for a Paidgroup"""
        self._check_group_id()

        relay = {
            "user": self.group.eth_addr,
            "group": self.group_id,
        }
        resp = self._post("https://prs-bp2.press.one/api/mvm/paidgroup/pay", relay)
        return resp.get("data")
