from tests import client

seed = client.group.create("mytest_configs")
client.group_id = seed["group_id"]


def test_basic():
    r = client.config.mode
    print("mode", r)
    assert "POST" in r

    r = client.config.allow_list
    print("allow_list", r)
    assert type(r) == list

    r = client.config.deny_list
    print("deny_list", r)

    assert type(r) == list


def test_update():
    r = client.config.trx_mode("POST")
    print(r)

    assert "TrxType" in r

    r = client.config.set_trx_mode("POST", "deny")
    print(r)

    r = client.config.set_mode("alw")
    print(r)
    assert r == None

    pubkey = client.group.pubkey
    r = client.config.update_allow_list(pubkey)
    print(r)
    assert "owner_pubkey" in r

    r = client.config.update_deny_list(pubkey)
    print(r)
    assert "owner_pubkey" in r

    test_basic()


def test_end():
    r = client.group.leave()
    print(r)


if __name__ == "__main__":
    test_basic()
    test_update()
    test_end()
