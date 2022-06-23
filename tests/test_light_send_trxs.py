import json

from rumpy import FullNode, LightNode

full = FullNode()
bot = LightNode()


def test_sends(app_key="group_timeline"):

    # create a new group by full node for test
    seed = full.api.create_group("mytest_send_trxs", app_key=app_key)
    assert "group_id" in seed

    # create new keypair to join the group.
    name_piece = seed["group_id"]
    bot.api.create_keypair(name_piece)
    params = {
        "seed": seed,
        "sign_alias": f"{name_piece}_sign",
        "encrypt_alias": f"{name_piece}_encrypt",
        "urls": ["https://127.0.0.1:51194"],
    }
    bot.api.join_group(**params)

    # light node send trxs to the group.
    group_id = seed["group_id"]

    resp = bot.api.send_note(group_id=group_id, content="content only text ")
    assert "trx_id" in resp

    trx_id = resp["trx_id"]

    resp = bot.api.send_note(group_id=group_id, content="text content with title", name="title")
    assert "trx_id" in resp

    trx_id2 = resp["trx_id"]

    try:
        resp = bot.api.send_note(group_id=group_id, name="title")
    except Exception as e:
        print(e)

    try:
        resp = bot.api.send_note(group_id=group_id, name="title", images=[])
    except Exception as e:
        print(e)

    resp = bot.api.send_note(
        group_id=group_id, name="title", images=[], content="content with text and title; no images"
    )
    assert "trx_id" in resp

    resp = bot.api.send_note(
        group_id=group_id, name="title", images=[r"D:\hi.jpg"], content="content with text and title and image"
    )
    assert "trx_id" in resp

    resp = bot.api.send_note(group_id=group_id, images=[r"D:\hi.jpg"], content="content with text and image")
    assert "trx_id" in resp

    resp = bot.api.send_note(group_id=group_id, images=[r"D:\hi.jpg"])
    assert "trx_id" in resp

    resp = bot.api.like(group_id=group_id, trx_id=trx_id)
    assert "trx_id" in resp

    try:
        resp = bot.api.like(group_id=group_id, trx_id=trx_id, content="hi")
    except Exception as e:
        print(e)

    resp = bot.api.dislike(group_id=group_id, trx_id=trx_id)
    assert "trx_id" in resp

    try:
        resp = bot.api.reply(group_id=group_id, trx_id=trx_id)
    except Exception as e:
        print(e)

    try:
        resp = bot.api.reply(group_id=group_id, content="re")
    except Exception as e:
        print(e)

    resp = bot.api.reply(group_id=group_id, trx_id=trx_id, content="reply with text")
    assert "trx_id" in resp

    resp = bot.api.reply(group_id=group_id, trx_id=trx_id, content="repley with image", images=[r"D:\hi.jpg"])
    assert "trx_id" in resp

    resp = bot.api.edit_note(
        group_id=group_id,
        trx_id=trx_id,
        content="edit a trx with text and image",
        images=[r"D:\hi.jpg"],
    )
    assert "trx_id" in resp

    resp = bot.api.del_note(group_id=group_id, trx_id=trx_id2)
    assert "trx_id" in resp


if __name__ == "__main__":
    test_sends("group_timeline")
    test_sends("group_post")
    test_sends("group_any")
