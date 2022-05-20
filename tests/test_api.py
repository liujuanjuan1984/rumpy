import dataclasses

import pytest

from tests import client, group_names_to_leave


class TestCase:
    def test_node(self):
        r = client.node.info
        assert dataclasses.is_dataclass(r)

        r0 = client.node.status
        assert r0.lower().find("online") >= 0

        r1 = client.group.create("mytest_pytest")
        assert "genesis_block" in r1
        client.group.join(r1)

        group_id = r1["group_id"]
        client.group_id = group_id
        r2 = client.group.is_joined()
        assert r2 == True

        client.group_id = group_id.replace(group_id[:5], "b" * 5)
        r3 = client.group.is_joined()
        assert r3 == False

        client.group_id = group_id
        r4 = client.node.groups_id
        assert client.group_id in r4

        client.group.leave()
        r5 = client.group.is_joined()
        assert r5 == False

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
            "owner_encryptpubkey": "age1y8ug7lw8ewauanaegynpnc5yqfrap9kzw49hwp6wrf2dcx0p8c8qexffqm",
            "consensus_type": "poa",
            "encryption_type": "public",
            "cipher_key": "3cdaaad37b20edb92ac5f2d505262ba5a27f0b0d650e5aa40d8231cd238c448b",
            "app_key": "group_timeline",
            "signature": "30450221009d00d86876d4e37b8408620dca823d0409afa03ae49c5c78526669f5d2a3c8fe022073cf3f3bbb19534614ae6d3eca65ac05d374909444825f59be44f1fe0fd1a0ca",
        }
        r = client.group.is_seed(seed)
        assert r == True
        r = client.group.join(seed)
        client.group_id = seed["group_id"]
        r = client.group.is_joined()
        assert r == True

    def test_leave_test_groups(self):

        r = client.group.create("mytest_test2")
        assert "group_id" in r

        data = {"group_name": "mytest_nihao3", "app_key": "group_note"}
        r = client.group.create(**data)
        assert "group_id" in r

        r = client.group.create(**{"group_name": "mytest_nihao3", "app_key": "group_note"})
        assert "group_id" in r

        for group_id in client.node.groups_id:
            client.group_id = group_id
            name = client.group.info().group_name

            if name.find("mytest_") >= 0 or name in group_names_to_leave:
                client.group.leave()

    def test_group(self):
        seed = client.group.create("mytest_pytest_group")
        assert "genesis_block" in seed

        client.group.join(seed)
        client.group_id = seed["group_id"]

        seed = client.group.seed()
        assert "genesis_block" in seed

        for i in range(10):
            kwargs = {"content": f"你好 {i}"}
            r5 = client.group.send_note(**kwargs)
            assert "trx_id" in r5

        trx_id = r5["trx_id"]
        kwargs = {"content": "回复一下", "inreplyto": trx_id}
        r6 = client.group.send_note(**kwargs)
        assert "trx_id" in r6

        # 发文
        resp = client.group.send_note(content="你好")
        assert "trx_id" in resp

        resp = client.group.send_note(content="nihao", images=["D:\\test-sample.png"])
        assert "trx_id" in resp

        resp = client.group.send_note(images=["D:\\test-sample.png"])
        assert "trx_id" in resp

        # 回复
        trx_id = resp["trx_id"]
        resp = client.group.reply("我回复你了", trx_id)
        assert "trx_id" in resp

        resp = client.group.send_note(content="nihao", images=[], inreplyto=trx_id)
        assert "trx_id" in resp

        resp = client.group.like(trx_id)
        assert "trx_id" in resp

        resp = client.group.dislike(trx_id)
        assert "trx_id" in resp

        trxs = client.group.content()
        try:
            trxtype = client.group.trx_type(trxs[-1])
            assert type(trxtype) == str
        except IndexError as e:
            print(e)
            pass

        trxs = client.group.all_content_trxs()

        resp = client.group.leave()
        r2 = client.group.is_joined()
        assert r2 == False

    def test_trx(self):

        gid = "4e784292-6a65-471e-9f80-e91202e3358c"
        client.group_id = gid
        bid = client.group.info().highest_block_id

        block = client.group.block(bid)
        assert "BlockId" in block

        trxs = block.get("Trxs", [])
        if len(trxs) > 0:
            tid = trxs[0]["TrxId"]
            x = client.group.trx(tid)
            assert "TrxId" in x

        trxs = client.group.content_trxs()
        assert len(trxs) >= 0

    def test_config(self):

        gid = client.group.create("mytest_config")["group_id"]
        client.group_id = gid
        r = client.config.mode

        r == {"TrxType": "POST", "AuthType": "FOLLOW_ALW_LIST"}
        r = client.config.set_trx_mode("post", "deny", "testit")
        r = client.config.set_trx_mode("post", "allow", "testit")
        r = client.config.allow_list
        r = client.config.deny_list

        r = client.config._update_list(
            "CAISIQIPfGufTgH4cQRGXUmZWbHshWdet0K5fMN1YR2NyKX33Q==",
            trx_types=[
                "POST",
                "ANNOUNCE",
                "REQ_BLOCK_FORWARD",
                "REQ_BLOCK_BACKWARD",
                "ASK_PEERID",
            ],
            mode="dny",
            memo="both in allow_list and deny_list",
        )

        r = client.config._update_list(
            "CAISIQIPfGufTgH4cQRGXUmZWbHshWdet0K5fMN1YR2NyKX33Q==",
            trx_types=[
                "POST",
                "ANNOUNCE",
                "REQ_BLOCK_FORWARD",
                "REQ_BLOCK_BACKWARD",
                "ASK_PEERID",
            ],
            mode="allow",
            memo="both in allow_list and deny_list",
        )

    def test_init(self):

        type(client.group)
        type(client.node)
        type(client.group_id)


if __name__ == "__main__":
    print(client.node.id)
    print(client.paid.dapp())
