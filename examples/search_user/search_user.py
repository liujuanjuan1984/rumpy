from typing import Dict, List
from rumpy import RumClient


class SearchUser(RumClient):
    def intrx(self, trx: Dict, xname):
        """
        搜寻昵称包含 xname 的用户，历史昵称也会搜索~
        返回 {pubkey:昵称} 作为结果
        """

        if trx["TypeUrl"] == "quorum.pb.Person":
            name = trx["Content"].get("name") or ""
            if name.lower().find(xname.lower()) >= 0:
                return {trx["Publisher"]: name}
        return {}

    def ingroup(self, xname) -> Dict:
        """
        搜寻昵称包含 xanme 的用户，历史记录也会搜寻到
        返回 {pubkey:[昵称]}
        """
        rlt = {}
        for trxdata in self.group.content():
            irlt = self.intrx(trxdata, xname)
            for pubkey in irlt:
                iname = irlt[pubkey]
                if pubkey not in rlt:
                    rlt[pubkey] = [iname]
                elif iname not in rlt[pubkey]:
                    rlt[pubkey].append(iname)
        return rlt

    def innode(self, xname):
        """
        搜寻昵称包含 xanme 的用户，历史记录也会搜寻到
        返回{group_id : {pubkey:[昵称]}
        """
        if not xname:
            raise ValueError("need piece of nickename to search.")
        rlt = {}
        for group_id in self.node.groups_id:
            self.group_id = group_id
            irlt = self.ingroup(xname)
            if len(irlt) > 0:
                rlt[group_id] = irlt
        return rlt
