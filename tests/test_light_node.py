from rumpy import LightNode

bot = LightNode(port=6002, crtfile=r"D:\Jupyter\quorum\dist\windows_amd64\certs\server.crt")


def test_keys():
    resp = bot.api.create_sign("my_sign")
    print(resp)

    resp = bot.api.create_encrypt("my_encrypt")
    print(resp)

    resp = bot.api.get_keys()
    print(resp)

    resp = bot.api.unbind_alias("my_signature")
    print(resp)  # done??

    # 无法改变 type 的值，是否不用传入??
    resp = bot.api.rebind_alias("mengmengda2", "7c39996f-4f36-48c4-b854-b69cc89f82a0", "encrypt")
    print(resp)

    resp = bot.api.get_keys()
    print(resp)


def test_groups():
    seed = {
        "genesis_block": {
            "BlockId": "883a30fa-98ed-48ec-98a6-e76aa41cbef3",
            "GroupId": "4e784292-6a65-471e-9f80-e91202e3358c",
            "ProducerPubKey": "CAISIQNK024r4gdSjIK3HoQlPbmIhDNqElIoL/6nQiYFv3rTtw==",
            "Hash": "zxemQb40qFA4dDbB2jXZ9kDYeyugBmyCE97FZU+STwQ=",
            "Signature": "MEYCIQCHgaOQw9rElx7xdxd4Q99arzVLJE20gE96HNakoKPhrgIhANjCdhohoQ/FvsvsPyxqiQeNuDGzLQ13B5iY1mAk7PI3",
            "TimeStamp": "1637574056648598000",
        },
        "group_id": "4e784292-6a65-471e-9f80-e91202e3358c",
        "group_name": "刘娟娟的朋友圈",
        "owner_pubkey": "CAISIQNK024r4gdSjIK3HoQlPbmIhDNqElIoL/6nQiYFv3rTtw==",
        "consensus_type": "poa",
        "encryption_type": "public",
        "cipher_key": "3cdaaad37b20edb92ac5f2d505262ba5a27f0b0d650e5aa40d8231cd238c448b",
        "app_key": "group_timeline",
        "signature": "30450221009d00d86876d4e37b8408620dca823d0409afa03ae49c5c78526669f5d2a3c8fe022073cf3f3bbb19534614ae6d3eca65ac05d374909444825f59be44f1fe0fd1a0ca",
    }
    sign_alias = "my_sign"
    encrypt_alias = "my_encrypt"
    urls = ["https://127.0.0.1:51194"]
    resp = bot.api.join_group(seed, sign_alias, encrypt_alias, urls)
    print(resp)

    resp = bot.api.get_keys()
    print(resp)

    resp = bot.api.list_groups()
    print(resp)

    resp = bot.api.group_info("4e784292-6a65-471e-9f80-e91202e3358c")
    print(resp)

    resp = bot.api.list_group("4e784292-6a65-471e-9f80-e91202e3358c")
    print(resp)

    resp = bot.api.seed("4e784292-6a65-471e-9f80-e91202e3358c")
    print(resp)

    resp = bot.api.content("4e784292-6a65-471e-9f80-e91202e3358c")
    print(resp)
    # {'error': 'Post "https://127.0.0.1:51194/api/v1/nodesdk/groupctn": x509: certificate signed by unknown authority (possibly because of "crypto/rsa: verification error" while trying to verify candidate authority certificate "*")'}

    resp = bot.api.send_note("4e784292-6a65-471e-9f80-e91202e3358c", content="大家好，这条来自轻节点")
    print(resp)


if __name__ == "__main__":
    test_keys()
    test_groups()
