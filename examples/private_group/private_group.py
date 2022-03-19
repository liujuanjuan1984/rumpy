import datetime
from rumpy import RumClient


class PrivateGroup(RumClient):
    def create(
        self,
        group_name,
        consensus_type="poa",
        encryption_type="private",
        app_key="group_timeline",
    ):
        relay = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }
        return self.group.create(**relay)

    def announce(self, memo):
        relay = {
            "group_id": self.group_id,
            "action": "add",
            "type": "user",
            "memo": memo,
        }
        return self.config.announce(**relay)

    def approve(self, pubkey):
        relay = {
            "user_pubkey": pubkey,
            "group_id": self.group_id,
            "action": "add",
        }
        return self.config.update_user(**relay)

    def users(self):
        return self.config.announced_users()
