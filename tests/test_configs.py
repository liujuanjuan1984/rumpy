from tests import client


def test_configs_view(group_id=None):

    client.group_id = group_id or client.group.create("mytest_configs")["group_id"]
    seed = client.group.seed()

    print("==== appconfig ====")
    r = client.config.keylist()
    print("keylist", r)

    for key in r:
        ik = client.config.key(key)
        print("key", key, ik)

    print("==== group info ====")

    r = seed["app_key"]
    print("app_key", r)

    r = seed["consensus_type"]
    print("consensus_type", r)

    r = seed["encryption_type"]
    print("encryption_type", r)

    print("==== user info ====")

    r = client.config.announced_users()
    print("announced_users", r)

    r = client.config.announced_producers()
    print("announced_producers", r)

    print("==== paid? ====")

    r = client.paid.dapp()
    print("dapp", r)

    r = client.paid.paidgroup()
    print("paidgroup", r)

    r = client.paid.payment()
    print("payment", r)


if __name__ == "__main__":
    print("Default configs of new group:")
    test_configs_view()
