from tests import client


def test_configs_view(group_id=None):
    group_id = group_id or client.api.create_group("mytest_configs")["group_id"]

    client.group_id = group_id
    seed = client.api.seed()

    print("==== appconfig ====")
    r = client.api.keylist()
    print("keylist", r)

    for key in r:
        ik = client.api.key(key)
        print("key", key, ik)

    """  seedimprove is update.
    print("==== group info ====")

    r = seed["app_key"]
    print("app_key", r)

    r = seed["consensus_type"]
    print("consensus_type", r)

    r = seed["encryption_type"]
    print("encryption_type", r)
    """

    print("==== user info ====")

    r = client.api.announced_users()
    print("announced_users", r)

    r = client.api.announced_producers()
    print("announced_producers", r)

    print("==== paid? ====")

    r = client.paid.dapp()
    print("dapp", r)

    r = client.paid.paidgroup()
    print("paidgroup", r)

    r = client.paid.payment()
    print("payment", r)

    r = client.api.update_profile(name="juanjuan", image=r"D:\png_files\test-sample.png")
    print(r)


if __name__ == "__main__":
    print("Default configs of new group:")
    test_configs_view()
