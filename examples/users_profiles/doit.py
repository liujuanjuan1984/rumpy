import os
from rumpy import RumClient

client = RumClient(port=58356)
client.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"

# give the file path or None to init it.
mydir = os.path.join(os.path.dirname(__file__), "data")
mytypes = ("name", "wallet", "image")
client.group.update_profiles(datadir=mydir, types=mytypes)
client.node.update_profiles(datadir=mydir, types=mytypes)
