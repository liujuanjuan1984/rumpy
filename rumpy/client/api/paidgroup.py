from .base import BaseAPI


class PaidGroup(BaseAPI):
    def _check_group_id(self):
        if self.group_id == None:
            raise ValueError("group_id is not set yet.")

    def _check_owner(self):
        if self.group.pubkey != self.group.owner:
            raise ValueError("you are not owner.")

    def dapp(self):
        """Get Info of Paidgroup DApp"""
        return self._get("https://prs-bp2.press.one/api/mvm/paidgroup")

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
        return self._post("https://prs-bp2.press.one/api/mvm/paidgroup/announce", relay)

    def group_info(self, group_id=None):
        """Get Detail of a Paidgroup"""
        return self._get(
            f"https://prs-bp2.press.one/api/mvm/paidgroup/{group_id or self.group_id}"
        )

    def pay(self):
        """Announce a Paidgroup"""
        self._check_group_id()

        relay = {
            "user": self.group.eth_addr,
            "group": self.group_id,
        }
        return self._post("https://prs-bp2.press.one/api/mvm/paidgroup/pay", relay)

    def paid(self):
        """Check Payment"""
        self._check_group_id()

        return self._get(
            f"https://prs-bp2.press.one/api/mvm/paidgroup/{self.group_id}/{self.group.eth_addr}"
        )
