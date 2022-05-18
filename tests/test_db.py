from rumpy.modules import *
from rumpy.module_op import BaseDB
from rumpy import RumClient

client = RumClient(port=58356)

client.db = BaseDB(
    "test_db",
    echo=True,
    reset=False,
)

client.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"

resp = client.group.send_note(content="早上好。")
if "trx_id" in resp:
    action = {
        "group_id": client.group_id,
        "trx_id": resp["trx_id"],
        "func": "client.group.send_note",
        "params": {"url": None, "relay": {"content": "早上好。"}},
    }
    client.db.add(Action(action))

print(resp)

actions = client.db.session.query(Action).all()
for action in actions:
    print(action.group_id, action.trx_id, action.func, action.params)
