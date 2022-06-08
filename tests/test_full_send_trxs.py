from rumpy import FullNode

bot = FullNode()


def test_sends(app_key="group_timeline"):
    resp = bot.api.create_group("mytest_send_trxs", app_key=app_key)
    assert "group_id" in resp
    seed = resp

    bot.group_id = seed["group_id"]

    resp = bot.api.send_note(content="hi")
    assert "trx_id" in resp

    trx_id = resp["trx_id"]

    resp = bot.api.send_note(content="hi，这条应该删掉", name="title")
    assert "trx_id" in resp

    trx_id2 = resp["trx_id"]

    try:
        resp = bot.api.send_note(name="title")
        assert "error" in resp
    except Exception as e:
        print(e)

    try:
        resp = bot.api.send_note(name="title", images=[])
        assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.send_note(name="title", images=[], content="hi a")
    assert "trx_id" in resp

    resp = bot.api.send_note(name="title", images=[r"D:\hi.jpg"], content="hi a")
    assert "trx_id" in resp

    resp = bot.api.send_note(images=[r"D:\hi.jpg"], content="hi a")
    assert "trx_id" in resp

    resp = bot.api.send_note(images=[r"D:\hi.jpg"])
    assert "trx_id" in resp

    resp = bot.api.like(trx_id=trx_id)
    assert "trx_id" in resp

    try:
        resp = bot.api.like(trx_id=trx_id, content="hi")
        assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.dislike(trx_id=trx_id)
    assert "trx_id" in resp

    try:
        resp = bot.api.reply(trx_id=trx_id)
        assert "error" in resp
    except Exception as e:
        print(e)

    try:
        resp = bot.api.reply(content="re")
        assert "error" in resp
    except Exception as e:
        print(e)

    resp = bot.api.reply(trx_id=trx_id, content="re")
    assert "trx_id" in resp

    resp = bot.api.reply(trx_id=trx_id, content="re", images=[r"D:\hi.jpg"])
    assert "trx_id" in resp

    resp = bot.api.edit_note(trx_id=trx_id, content="change it", images=[r"D:\hi.jpg"])
    assert "trx_id" in resp

    resp = bot.api.del_note(trx_id=trx_id2)
    assert "trx_id" in resp


if __name__ == "__main__":
    test_sends("group_timeline")
    test_sends("group_post")
    test_sends("group_any")
