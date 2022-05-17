class BaseAPI:
    def __init__(self, client=None):
        self._client = client

    def _get(self, path: str, relay={}, api_base=None):
        return self._client.get(path, relay, api_base)

    def _post(self, path: str, relay={}, api_base=None):
        return self._client.post(path, relay, api_base)

    @property
    def group_id(self):
        return self._client.group_id

    @property
    def node(self):
        return self._client.node

    @property
    def group(self):
        return self._client.group

    def _check_group_id(self):
        if self.group_id == None:
            raise ValueError("group_id is not set yet.")

    def _check_owner(self):
        if self.group.pubkey != self.group.owner:
            raise ValueError("you are not owner.")
