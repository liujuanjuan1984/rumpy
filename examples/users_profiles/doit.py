import os
from rumpy import RumClient
from users_profiles import *

client = RumClient(port=58356)
client.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"

# give the file path or None to init it.
mydir = os.path.join(os.path.dirname(__file__), "data")

update_profiles(
    client,
    users_data=None,
    users_profiles_file=None,
    users_profiles_dir=mydir,
    profile_types=("name", "wallet", "image"),
)
update_node_profiles(client, users_profiles_dir=mydir, profile_types=("name", "wallet", "image"))
