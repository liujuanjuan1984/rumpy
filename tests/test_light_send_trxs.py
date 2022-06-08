import json

from rumpy import FullNode, LightNode

full = FullNode()
bot = LightNode()


def test_sends(app_key="group_timeline"):
    resp = full.api.create_group("mytest_send_trxs", app_key=app_key)
    print(resp)
    # assert "group_id" in resp
    seed = resp

    bot.api.create_keypair("juanjuan")
    params = {
        "seed": seed,
        "sign_alias": "juanjuan_sign",
        "encrypt_alias": "juanjuan_encrypt",
        "urls": ["https://127.0.0.1:51194"],
    }
    bot.api.join_group(**params)

    group_id = seed["group_id"]

    resp = bot.api.send_note(group_id=group_id, content="hi")
    print(resp)
    # assert "trx_id" in resp

    resp = json.loads(resp.replace("\n", ""))
    trx_id = resp["trx_id"]

    resp = bot.api.send_note(group_id=group_id, content="hi，这条应该删掉", name="title")
    print(resp)
    # assert "trx_id" in resp

    resp = json.loads(resp.replace("\n", ""))
    trx_id2 = resp["trx_id"]

    try:
        resp = bot.api.send_note(group_id=group_id, name="title")
        print(resp)
        # assert "error" in resp
    except Exception as e:
        print(e)

    try:
        resp = bot.api.send_note(group_id=group_id, name="title", images=[])
        print(resp)
        # assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.send_note(group_id=group_id, name="title", images=[], content="hi a")
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.send_note(group_id=group_id, name="title", images=[r"D:\hi.jpg"], content="hi a")
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.send_note(group_id=group_id, images=[r"D:\hi.jpg"], content="hi a")
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.send_note(group_id=group_id, images=[r"D:\hi.jpg"])
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.like(group_id=group_id, trx_id=trx_id)
    print(resp)
    # assert "trx_id" in resp

    try:
        resp = bot.api.like(group_id=group_id, trx_id=trx_id, content="hi")
        print(resp)
        # assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.dislike(group_id=group_id, trx_id=trx_id)
    print(resp)
    # assert "trx_id" in resp

    try:
        resp = bot.api.reply(group_id=group_id, trx_id=trx_id)
        print(resp)
        # assert "error" in resp
    except Exception as e:
        print(e)

    try:
        resp = bot.api.reply(group_id=group_id, content="re")
        print(resp)
        # assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.reply(group_id=group_id, trx_id=trx_id, content="re")
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.reply(group_id=group_id, trx_id=trx_id, content="re", images=[r"D:\hi.jpg"])
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.edit_note(
        group_id=group_id,
        trx_id=trx_id,
        content="change it",
        images=[r"D:\hi.jpg"],
    )
    print(resp)
    # assert "trx_id" in resp

    resp = bot.api.del_note(group_id=group_id, trx_id=trx_id2)
    print(resp)
    # assert "trx_id" in resp


if __name__ == "__main__":
    test_sends("group_timeline")
    test_sends("group_post")
    test_sends("group_any")
