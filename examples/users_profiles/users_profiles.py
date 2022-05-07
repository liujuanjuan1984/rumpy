import datetime
from rumpy import RumClient
from officy import JsonFile, Stime


class UsersProfiles(RumClient):
    def update(self, users_profiles_file=None):
        users_profiles_file = None or f"users_profiles_group_{self.group_id}.json"
        users_data = JsonFile(users_profiles_file).read({})

        trx_id = users_data.get("trx_id")
        trxs = self.group.all_content_trxs(trx_id=trx_id)

        profile_trxs = []
        for trx in trxs:
            if trx.get("TypeUrl") == "quorum.pb.Person":
                profile_trxs.append(trx)

        if "group_id" not in users_data:
            users_data["group_id"] = self.group_id

        if "group_name" not in users_data:
            users_data["group_name"] = self.group.seed()["group_name"]

        # trx_id: record the progress to get new trxs
        if "trx_id" not in users_data:
            users_data["trx_id"] = trxs[-1]["TrxId"] if len(trxs) > 0 else trx_id

        users = users_data.get("data") or {}

        for trx in profile_trxs:
            pubkey = trx["Publisher"]
            if pubkey not in users:
                users[pubkey] = {"creat_at": str(datetime.datetime.now())}
            for key in trx["Content"]:
                users[pubkey].update({key: trx["Content"][key]})
            ts = str(Stime.ts2datetime(trx["TimeStamp"]))
            users[pubkey].update({"update_at": ts})

        users_data.update({"data": users})
        JsonFile(users_profiles_file).write(users_data)
        print(datetime.datetime.now(), "update is done.", users_profiles_file)
        return users
