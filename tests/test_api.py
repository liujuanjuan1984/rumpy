import dataclasses

import pytest

import rumpy.utils as utils
from tests import client, group_names_to_leave


class TestCase:
    def test_node(self):
        r = client.api.node_info
        assert dataclasses.is_dataclass(r)

        r0 = client.api.node_status
        assert r0.lower().find("online") >= 0

        r1 = client.api.create_group("mytest_pytest")
        assert "group_id" in r1
        client.api.join_group(r1)

        group_id = r1["group_id"]
        client.group_id = group_id
        r2 = client.api.is_joined()
        assert r2 == True

        client.group_id = group_id.replace(group_id[:5], "b" * 5)
        r3 = client.api.is_joined()
        assert r3 == False

        client.group_id = group_id
        r4 = client.api.groups_id
        assert client.group_id in r4

        client.api.leave_group()
        r5 = client.api.is_joined()
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
        r = utils.is_seed(seed)
        assert r == True
        r = client.api.join_group(seed)
        client.group_id = seed["group_id"]
        r = client.api.is_joined()
        assert r == True

    def test_leave_test_groups(self):

        r = client.api.create_group("mytest_test2")
        assert "group_id" in r

        data = {"group_name": "mytest_nihao3", "app_key": "group_note"}
        r = client.api.create_group(**data)
        assert "group_id" in r

        r = client.api.create_group(**{"group_name": "mytest_nihao3", "app_key": "group_note"})
        assert "group_id" in r

        for group_id in client.api.groups_id:
            client.group_id = group_id
            name = client.api.group_info().group_name

            if name.find("mytest_") >= 0 or name in group_names_to_leave:
                # client.api.leave_group()
                pass

    def test_group(self):
        seed = client.api.create_group("mytest_pytest_group")
        assert "group_id" in seed

        client.api.join_group(seed)
        client.group_id = seed["group_id"]

        seed = client.api.seed()
        assert type(seed) == dict

        for i in range(10):
            kwargs = {"content": f"你好 {i}"}
            r5 = client.api.send_note(**kwargs)
            assert "trx_id" in r5

        trx_id = r5["trx_id"]
        kwargs = {"content": "回复一下", "trx_id": trx_id}
        r6 = client.api.reply(**kwargs)
        assert "trx_id" in r6

        # 发文
        resp = client.api.send_note(content="你好")
        assert "trx_id" in resp

        resp = client.api.send_note(content="nihao", images=["D:\\png_files\\test-sample.png"])
        assert "trx_id" in resp

        resp = client.api.send_note(images=["D:\\png_files\\test-sample.png"])
        assert "trx_id" in resp

        # 回复
        trx_id = resp["trx_id"]
        resp = client.api.reply("我回复你了", trx_id)
        assert "trx_id" in resp

        resp = client.api.reply(content="nihao", images=[], trx_id=trx_id)
        assert "trx_id" in resp

        resp = client.api.like(trx_id)
        assert "trx_id" in resp

        resp = client.api.dislike(trx_id)
        assert "trx_id" in resp

        resp = client.api.leave_group()
        r2 = client.api.is_joined()
        assert r2 == False

    def test_trx(self):

        gid = "4e784292-6a65-471e-9f80-e91202e3358c"
        client.group_id = gid
        bid = client.api.group_info().highest_block_id

        block = client.api.block(bid)
        assert "BlockId" in block

        trxs = block.get("Trxs", [])
        if len(trxs) > 0:
            tid = trxs[0]["TrxId"]
            x = client.api.trx(trx_id=tid)
            assert "TrxId" in x

        trxs = client.api.get_group_content()
        assert len(trxs) >= 0

    def test_config(self):

        gid = client.api.create_group("mytest_config")["group_id"]
        client.group_id = gid
        r = client.api.mode

        r == {"TrxType": "POST", "AuthType": "FOLLOW_ALW_LIST"}
        r = client.api.set_trx_mode("post", "deny", "testit")
        r = client.api.set_trx_mode("post", "allow", "testit")
        r = client.api.allow_list
        r = client.api.deny_list

        r = client.api._update_list(
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

        r = client.api._update_list(
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

        type(client.api)
        type(client.group_id)


if __name__ == "__main__":
    print(client.api.node_id)
    print(client.paid.dapp())
