from tests import client

seed = client.api.create_group("mytest_paidgroup")
client.group_id = seed["group_id"]


def test_basic():
    r = type(client.paid)
    print(r)

    r = dir(client.paid)

    print(r)
    assert "paidgroup" in r

    r = client.paid.dapp()

    print(r)
    assert "asset" in r

    r = client.paid.paidgroup()
    print(r)
    assert r == None

    r = client.paid.payment()
    print(r)
    assert r == None


def test_update():
    r = client.paid.announce(1, 99)
    print(r)
    assert "qrcode" in r
    print(r.get("qrcode"))

    r = client.paid.pay()
    print(r)
    assert "error" in r

    r = client.paid.payment()
    print(r)


def test_end():
    client.api.leave_group()


if __name__ == "__main__":
    test_basic()
    test_update()
    test_end()
