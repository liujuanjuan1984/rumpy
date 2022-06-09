from rumpy import FullNode

client = FullNode()

seed = client.api.create_group("mytest_configs")
client.group_id = seed["group_id"]


def test_basic():
    r = client.api.mode
    print("mode", r)
    assert "POST" in r

    r = client.api.allow_list
    print("allow_list", r)
    assert type(r) == list

    r = client.api.deny_list
    print("deny_list", r)

    assert type(r) == list


def test_update():
    r = client.api.trx_mode("POST")
    print(r)

    assert "TrxType" in r

    r = client.api.set_trx_mode("POST", "deny")
    print(r)

    r = client.api.set_mode("alw")
    print(r)
    assert r == None

    pubkey = client.api.pubkey
    r = client.api.update_allow_list(pubkey)
    print(r)
    assert "owner_pubkey" in r

    r = client.api.update_deny_list(pubkey)
    print(r)
    assert "owner_pubkey" in r

    test_basic()


if __name__ == "__main__":
    test_basic()
    test_update()
