class BaseAPI:
    def __init__(self, client=None):
        self._client = client

    def check_group_id_required(self):
        if self._client.group_id == None:
            raise ValueError("client.group_id is required, now it's None.")

    def check_owner_required(self):
        if self._client.group.pubkey != self._client.group.owner:
            raise ValueError("you are not the owner of the group.")
