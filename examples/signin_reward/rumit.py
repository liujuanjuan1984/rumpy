import datetime
from rumpy import RumClient
from rumpy.client.utiltools import ts2datetime


class Rumit(RumClient):
    def wallets(self):
        """get the wallets info of the group.

        Returns:
            {
                pubkey:{
                    "name": name_string,
                    "wallet": mixin_wallet_id,
                }
            }
        """
        wallets = self.group.get_users_profiles(
            {},
            (
                "name",
                "wallet",
            ),
        )
        wallets_info = {}
        for pubkey in wallets["data"]:
            if "wallet" in wallets["data"][pubkey]:
                name = wallets["data"][pubkey].get("name") or pubkey[-10:-2]
                wallet = wallets["data"][pubkey]["wallet"][0]["id"]
                wallets_info[pubkey] = {"name": name, "wallet": wallet}
        return wallets_info

    def counts(self, days=-1, num=100):
        """counts trxs num of every pubkey published at that day.

        Args:
            days (int, optional): days of datetime.timedata. Defaults to -1 which means yesterday.
            num (int, optional): how many trxs to check once. Defaults to 100.

        Returns:
            {
                "data":{pubkey:num},
                "date": that_day_string
            }
        """

        thatday = datetime.datetime.now().date() + datetime.timedelta(days=days)

        while True:
            _trxs = self.group.content_trxs(is_reverse=True, num=num)
            lastest_day = ts2datetime(_trxs[-1]["TimeStamp"]).date()
            if lastest_day < thatday:
                counts = {}
                for _trx in _trxs:
                    _day = ts2datetime(_trx["TimeStamp"]).date()
                    if _day == thatday:
                        _pubkey = _trx["Publisher"]
                        if _pubkey not in counts:
                            counts[_pubkey] = 1
                        else:
                            counts[_pubkey] += 1
                else:
                    counts_result = {"data": counts, "date": str(thatday)}
                break
            else:
                num += num

        return counts_result

    def rewards(self, n=1, days=-1, wallets_info=None, counts_result=None):
        """get the to_rewards info.

        Args:
            n (int, optional): how many trxs sent at that day by one pubkey who should be rewards? Defaults to 1.
            days (int, optional): days of datetime.timedata. Defaults to -1 which means yesterday.
            wallets_info (dict, optional):. Defaults to None.
            counts_result (dict, optional):. Defaults to None.

        Returns:
            {
                "group_id": group_id,
                "date": that_day_string,
                "data":{
                    mixin_wallet_id:{
                        "pubkey":pubkey,
                        "wallet":mixin_wallet_id,
                        "name":user_nickname_in_the_rum_group,
                        "num":users_trxs_num_at_that_day,
                        }
                    }
            }
        """
        wallets_info = wallets_info or self.wallets()
        counts_result = counts_result or self.counts(days=days)
        to_rewards = {}
        for pubkey in counts_result["data"]:
            if counts_result["data"][pubkey] >= n:
                if pubkey in wallets_info:
                    wellet = wallets_info[pubkey].get("wallet")
                    name = wallets_info[pubkey].get("name")
                    to_rewards[wellet] = {
                        "pubkey": pubkey,
                        "wallet": wellet,
                        "name": name,
                        "num": counts_result["data"][pubkey],
                    }

        thatday = datetime.datetime.now().date() + datetime.timedelta(days=days)
        return {
            "group_id": self.group_id,
            "date": str(thatday),
            "data": to_rewards,
        }
