import os

from officy import JsonFile

from rumpy import FullNode

client = FullNode(port=62663)
group_id = "4e784292-6a65-471e-9f80-e91202e3358c"

# give the file path or None to init it.
mydir = os.path.join(os.path.dirname(__file__), "data")
mytypes = ("name", "wallet")


def group_update_profiles(
    client,
    group_id,
    users_data=None,
    users_profiles_file=None,
    datadir=None,
    types=("name", "wallet", "image"),
):
    client.group_id = group_id
    if users_data:
        return client.api.get_users_profiles(users_data, types)

    filename = f"users_profiles_group_{client.group_id}.json"
    if datadir:
        users_profiles_file = os.path.join(datadir, filename)
    else:
        users_profiles_file = users_profiles_file or filename

    users_data = JsonFile(users_profiles_file).read({})
    users_data = client.api.get_users_profiles(users_data, types)

    JsonFile(users_profiles_file).write(users_data)
    return users_data


def node_update_profiles(client, datadir, types=("name", "wallet", "image")):
    for gid in client.api.groups_id:
        client.group_id = gid
        group_update_profiles(client, group_id=gid, datadir=datadir, types=types)


group_update_profiles(client, group_id=group_id, datadir=mydir, types=mytypes)

node_update_profiles(client, datadir=mydir, types=mytypes)
