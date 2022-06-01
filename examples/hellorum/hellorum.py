import datetime
import os

from rumpy import FullNode


def main():

    client = FullNode(port=51194)

    # create group for test
    seed = client.group.create("mytest_hellorum")
    client.group_id = seed["group_id"]

    # post to group
    payload = {"content": f"{str(datetime.datetime.now())} hello rum"}
    resp1 = client.group.send_note(**payload)
    print(resp1)

    payload = {
        "content": f"{str(datetime.datetime.now())} hello again.can  u see the picture i posted?",
        "images": [os.path.join(os.path.dirname(__file__), "girl.png")],
    }
    resp2 = client.group.send_note(**payload)
    print(resp2)

    payload = {
        "content": f"{str(datetime.datetime.now())} reply to hello rum ",
        "inreplyto": resp1["trx_id"],
    }
    resp3 = client.group.send_note(**payload)
    print(resp3)

    payload = {
        "content": f"{str(datetime.datetime.now())} reply to  post with picture",
        "inreplyto": resp2["trx_id"],
    }
    resp4 = client.group.send_note(**payload)
    print(resp4)

    payload = {
        "content": f"{str(datetime.datetime.now())} this is reply to reply",
        "inreplyto": resp4["trx_id"],
    }
    resp5 = client.group.send_note(**payload)
    print(resp5)
    # like
    client.group.like(resp1["trx_id"])
    client.group.like(resp2["trx_id"])
    client.group.like(resp3["trx_id"])
    client.group.like(resp4["trx_id"])
    client.group.like(resp5["trx_id"])

    # dislike
    client.group.dislike(resp1["trx_id"])

    # group info
    info = client.group.info()
    print(info.__dict__)

    # node info
    print(client.node.id)
    print(client.node.status)


if __name__ == "__main__":
    main()
