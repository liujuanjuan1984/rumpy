import datetime
import os
from officy import JsonFile, Stime
from typing import Dict, List


def update_group_profiles(client, users_data: Dict, profile_types=("name", "image", "wallet")):

    # get new trxs from the trx_id
    trx_id = users_data.get("trx_id")
    trxs = client.group.all_content_trxs(trx_id=trx_id)

    # update trx_id: to record the progress to get new trxs
    if len(trxs) > 0:
        to_tid = trxs[-1]["TrxId"]
    else:
        to_tid = trx_id

    users_data.update(
        {
            "group_id": client.group_id,
            "group_name": client.group.seed()["group_name"],
            "trx_id": to_tid,
            "update_at": str(datetime.datetime.now()),
        }
    )

    users = users_data.get("data") or {}
    profile_trxs = [trx for trx in trxs if trx.get("TypeUrl") == "quorum.pb.Person"]

    for trx in profile_trxs:
        pubkey = trx["Publisher"]
        if pubkey not in users:
            users[pubkey] = {"creat_at": str(datetime.datetime.now())}
        for key in trx["Content"]:
            if key in profile_types:
                users[pubkey].update({key: trx["Content"][key]})
                ts = str(Stime.ts2datetime(trx["TimeStamp"]))
                users[pubkey].update({"update_at": ts})

    users_data.update({"data": users})
    return users_data


def update_profiles(
    client,
    users_data=None,
    users_profiles_file=None,
    users_profiles_dir=None,
    profile_types=("name", "wallet", "image"),
):

    if users_data:
        return update_group_profiles(client, users_data, profile_types)

    filename = f"users_profiles_group_{client.group_id}.json"
    if users_profiles_dir:
        users_profiles_file = os.path.join(users_profiles_dir, filename)
    else:
        users_profiles_file = users_profiles_file or filename

    users_data = JsonFile(users_profiles_file).read({})
    users_data = update_group_profiles(client, users_data, profile_types)

    JsonFile(users_profiles_file).write(users_data)
    return users_data


def update_node_profiles(client, users_profiles_dir, profile_types=("name", "wallet", "image")):
    for gid in client.node.groups_id:
        client.group_id = gid
        update_profiles(client, users_profiles_dir=users_profiles_dir, profile_types=profile_types)
