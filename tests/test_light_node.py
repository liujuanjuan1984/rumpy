from rumpy import LightNode

bot = LightNode()
full_node_urls = ["https://127.0.0.1:51194"]


def test_keys():
    resp = bot.api.create_keypair("my")
    print(resp)

    resp = bot.api.keys()
    print(resp)


def test_keys_v2():
    resp = bot.api.remove_alias("my_signature")
    print(resp)  # done??

    resp = bot.api.remove_alias("mengmengda2")
    print(resp)

    resp = bot.api.keys()
    print(resp)


def test_groups():
    seed = {
        "genesis_block": {
            "BlockId": "edb5b7ab-6173-45c5-b384-97d68861a358",
            "GroupId": "1b26b056-30af-4720-a4d2-706773cc497f",
            "ProducerPubKey": "CAISIQPPqheIjREZKG8VgwNxHWoivJxtjptKaSTWt2Q96VtBCw==",
            "Hash": "hAHKzkMd+pwir0/NFYGCLMnl9gNsaWYCoHXjkBgwWtA=",
            "Signature": "MEYCIQC4QCHV7FNNG+ZYf7UL3xdqr2wzCwq92Ix4MiBeBC9eUgIhANCfsOxuMqJGUNenRRLlTZqbCIUYspnvUuLVg+lfe1RM",
            "TimeStamp": "1654683030376047400",
        },
        "group_id": "1b26b056-30af-4720-a4d2-706773cc497f",
        "group_name": "不要删，本地测试用",
        "owner_pubkey": "CAISIQPPqheIjREZKG8VgwNxHWoivJxtjptKaSTWt2Q96VtBCw==",
        "consensus_type": "poa",
        "encryption_type": "public",
        "cipher_key": "31b6a83b3e3cec0f13f5234f50e296d0d5130d2d209c03674f347ce7b82e0e2f",
        "app_key": "group_timeline",
        "signature": "30450220548be4cbb73fd19317a99e937d544760cfb3f66441288551d1ce79b7e52414d9022100b479aceef38c35a423b82757592190326a07f65bda68229ccebdb2062800f477",
    }
    sign_alias = "my_sign"
    encrypt_alias = "my_encrypt"
    urls = full_node_urls
    print(urls)
    resp = bot.api.join_group(seed, sign_alias, encrypt_alias, urls)
    print(resp)

    resp = bot.api.keys()
    print(resp)

    resp = bot.api.groups()
    print(resp)

    resp = bot.api.group_info("1b26b056-30af-4720-a4d2-706773cc497f")
    print(resp)

    resp = bot.api.group("1b26b056-30af-4720-a4d2-706773cc497f")
    print(resp)

    resp = bot.api.seed(group_id="1b26b056-30af-4720-a4d2-706773cc497f")
    print(resp)

    resp = bot.api.get_group_content(group_id="1b26b056-30af-4720-a4d2-706773cc497f")
    print(resp)

    resp = bot.api.send_note(group_id="1b26b056-30af-4720-a4d2-706773cc497f", content="大家好，这条来自轻节点")
    print(resp)


if __name__ == "__main__":
    """
    #test_keys()
    #test_groups()
    #resp = bot.api.content("1b26b056-30af-4720-a4d2-706773cc497f",reverse=True,num=3,start_trx="22a910b2-caea-4f68-a405-8a21db46f2ad")
    resp = bot.api.trx("1b26b056-30af-4720-a4d2-706773cc497f","4e672e38-1f74-4ba2-bc14-1c16e9a7f189")
    print(resp)
    #resp = bot.api.send_note("1b26b056-30af-4720-a4d2-706773cc497f", content="[debug]这条来自轻节点")
    resp = bot.api.trx("1b26b056-30af-4720-a4d2-706773cc497f","b32edf8d-c7b1-4abb-b3d3-f7ffa1ebe22b")
    resp = bot.api.groups()
    resp = bot.api.block(group_id,block_id)
    """

    group_id = "1b26b056-30af-4720-a4d2-706773cc497f"
    block_id = "7adf9dab-4730-4734-8570-40ed6e6e842a"
    trx_id = "604dc47f-636b-4e5f-a70a-92dd55e148d5"
    resp = bot.api.trx(group_id=group_id, trx_id=trx_id)
    print(resp)
