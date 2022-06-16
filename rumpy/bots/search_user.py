import logging

logger = logging.getLogger(__name__)


class SearchUser:
    """bot: search pubkeys in all-history-nicknames for those containing with the piece: name_fragment"""

    def __init__(self, rum_client, name_fragment: str):
        self.rum = rum_client

        if type(name_fragment) != str:
            raise ValueError("param:name_fragment type error. It should be string.")
        if len(name_fragment) < 2:
            raise ValueError("param:name_fragment is too short! Give something to search.")
        self.name_fragment = name_fragment.lower()

    def search_in_trx(self, trx):
        """returns:pubkey,nickname"""
        pubkey = False
        name = trx["Content"].get("name")
        if name and name.lower().find(self.name_fragment) >= 0:
            pubkey = trx["Publisher"]
        logger.debug(f"search in trx <{trx['TrxId']}>: <{name}>")
        return pubkey, name

    def search_in_group(self, group_id, trx_id=None, group_rlt=None):
        """search in group starting from the trx_id default to be None. which means searching from the beginning.

        returns:
        group_rlt: {pubkey:[nickname1,nickname2]}
        progress_tid: trx_id
        """
        logger.debug(f"search in group <{group_id}> start from trx: <{trx_id}>")

        group_rlt = group_rlt or {}
        trxs = self.rum.api.get_group_all_contents(group_id=group_id, trx_id=trx_id, trx_types=("person",))

        progress_tid = trx_id
        for trx in trxs:
            pubkey, name = self.search_in_trx(trx)
            progress_tid = trx["TrxId"]
            if not pubkey:
                continue
            if pubkey not in group_rlt:
                group_rlt[pubkey] = [name]
            if name not in group_rlt[pubkey]:
                group_rlt[pubkey].append(name)
        return progress_tid, group_rlt

    def search_in_node(self, progress=None, rlt=None):
        """
        progress: {group_id:trx_id} #已搜索至的 trx_id
        rlt: {group_id : {pubkey:[name,name]}} #pubkey及包含该昵称片段的昵称全称
        """
        progress = progress or {}
        rlt = rlt or {}

        for group_id in self.rum.api.groups_id:
            if group_id not in rlt:
                rlt[group_id] = {}
            if group_id not in progress:
                progress[group_id] = {}
            trx_id = progress[group_id].get("trx_id")
            progress_tid, group_rlt = self.search_in_group(group_id, trx_id, rlt[group_id])
            progress[group_id] = {"group_id": group_id, "trx_id": progress_tid}
            rlt[group_id] = group_rlt

        return progress, rlt

    def io_with_file(self, data_dir=None):
        import os

        from officy import JsonFile

        data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        progress_file = os.path.join(data_dir, f"search_user_{self.name_fragment}_progress.json")
        rlt_file = os.path.join(data_dir, f"search_user_{self.name_fragment}.json")
        progress = JsonFile(progress_file).read({})
        rlt = JsonFile(rlt_file).read({})
        progress, rlt = self.search_in_node(progress, rlt)
        JsonFile(progress_file).write(progress)
        JsonFile(rlt_file).write(rlt)

    def io_with_db(self):  # TODO:
        pass


if __name__ == "__main__":
    from rumpy import FullNode

    rum = FullNode()
    SearchUser(rum, "huoju").io_with_file(data_dir=r"D:\Jupyter\rumpy\rum_whosays\whosays\data")
