class BaseAPI:
    def __init__(self, client=None):
        self._client = client

    def _get(self, url: str, relay={}):
        return self._client.get(url, relay)

    def _post(self, url: str, relay={}):
        return self._client.post(url, relay)

    @property
    def baseurl(self) -> str:
        return self._client.baseurl

    @property
    def baseurl_app(self) -> str:
        return self._client.baseurl_app

    @property
    def group_id(self):
        return self._client.group_id

    @property
    def node(self):
        return self._client.node

    @property
    def group(self):
        return self._client.group

    @property
    def db(self):
        return self._client.db

    def _check_group_id(self):
        if self.group_id == None:
            raise ValueError("group_id is not set yet.")

    def _check_owner(self):
        if self.group.pubkey != self.group.owner:
            raise ValueError("you are not owner.")
