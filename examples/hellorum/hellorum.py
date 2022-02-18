import datetime
import os
from rumpy import RumClient
from rumpyconfig import RumpyConfig


def main():

    client = RumClient(**RumpyConfig.GUI)

    # create group for test
    seed = client.group.create("mytest_hellorum")
    group_id = seed["group_id"]

    # post to group
    relay = {"content": f"{str(datetime.datetime.now())} hello rum"}
    resp1 = client.group.send_note(group_id, **relay)

    relay = {
        "content": f"{str(datetime.datetime.now())} hello again.can  u see the picture i posted?",
        "image": [os.path.join(os.path.dirname(__file__), "girl.png")],
    }
    resp2 = client.group.send_note(group_id, **relay)

    relay = {
        "content": f"{str(datetime.datetime.now())} reply to hello rum ",
        "inreplyto": resp1["trx_id"],
    }
    resp3 = client.group.send_note(group_id, **relay)

    relay = {
        "content": f"{str(datetime.datetime.now())} reply to  post with picture",
        "inreplyto": resp2["trx_id"],
    }
    resp4 = client.group.send_note(group_id, **relay)

    relay = {
        "content": f"{str(datetime.datetime.now())} thi is reply to reply",
        "inreplyto": resp4["trx_id"],
    }
    resp5 = client.group.send_note(group_id, **relay)

    # like
    client.group.like(group_id, resp1["trx_id"])
    client.group.like(group_id, resp2["trx_id"])
    client.group.like(group_id, resp3["trx_id"])
    client.group.like(group_id, resp4["trx_id"])
    client.group.like(group_id, resp5["trx_id"])

    # dislike
    client.group.dislike(group_id, resp1["trx_id"])

    # group info
    info = client.group.info(group_id)
    print(info)

    # node info
    print(client.node.id)
    print(client.node.status)


if __name__ == "__main__":
    main()
