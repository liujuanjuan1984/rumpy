import datetime
import os

from rumpy import FullNode


def main():

    client = FullNode(port=62663)

    # create group for test
    seed = client.api.create_group("mytest_hellorum")
    client.group_id = seed["group_id"]

    # post to group
    payload = {"content": f"{str(datetime.datetime.now())} hello rum"}
    resp1 = client.api.send_note(**payload)
    print(resp1)

    payload = {
        "content": f"{str(datetime.datetime.now())} hello again.can  u see the picture i posted?",
        "images": [os.path.join(os.path.dirname(__file__), "girl.png")],
    }
    resp2 = client.api.send_note(**payload)
    print(resp2)

    payload = {
        "content": f"{str(datetime.datetime.now())} reply to hello rum ",
        "inreplyto": resp1["trx_id"],
    }
    resp3 = client.api.send_note(**payload)
    print(resp3)

    payload = {
        "content": f"{str(datetime.datetime.now())} reply to  post with picture",
        "inreplyto": resp2["trx_id"],
    }
    resp4 = client.api.send_note(**payload)
    print(resp4)

    payload = {
        "content": f"{str(datetime.datetime.now())} this is reply to reply",
        "inreplyto": resp4["trx_id"],
    }
    resp5 = client.api.send_note(**payload)
    print(resp5)
    # like
    client.api.like(resp1["trx_id"])
    client.api.like(resp2["trx_id"])
    client.api.like(resp3["trx_id"])
    client.api.like(resp4["trx_id"])
    client.api.like(resp5["trx_id"])

    # dislike
    client.api.dislike(resp1["trx_id"])

    # group info
    info = client.api.group_info()
    print(info.__dict__)

    # node info
    print(client.api.node_id)
    print(client.api.node_status)


if __name__ == "__main__":
    main()
