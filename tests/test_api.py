import pytest
from rumpy import RumClient
from officepy import JsonFile
from config import Config
import dataclasses

client = RumClient(**Config.CLIENT_PARAMS["gui"])


class TestCase:
    def test_api(self):

        r = client.node.info
        assert dataclasses.is_dataclass(r)

        r0 = client.node.status
        assert r0.lower().find("online") >= 0

        r1 = client.node.create_group("新增测试组")
        assert "genesis_block" in r1
        client.node.join_group(r1)

        group_id = r1["group_id"]
        r2 = client.node.is_joined(group_id)
        assert r2 == True

        seed = client.group.seed(group_id)
        assert "genesis_block" in seed

        r3 = client.node.is_joined(group_id.replace(group_id[:5], "b" * 5))
        assert r3 == False

        r4 = client.node.groups_id
        assert group_id in r4

        for i in range(10):
            kwargs = {"content": f"你好 {i}"}
            r5 = client.group.send_note(group_id, **kwargs)
            assert "trx_id" in r5

        trx_id = r5["trx_id"]
        kwargs = {"content": "回复一下", "inreplyto": trx_id}
        r6 = client.group.send_note(group_id, **kwargs)
        assert "trx_id" in r6

        # 发文
        resp = client.group.send_note(group_id, content="你好")
        assert "trx_id" in resp

        resp = client.group.send_note(group_id, content="", image=[])
        assert "trx_id" not in resp

        resp = client.group.send_note(group_id, image=["D:\\test-sample.png"])
        assert "trx_id" in resp

        # 回复
        trx_id = resp["trx_id"]
        resp = client.group.reply(group_id, "我回复你了", trx_id)
        assert "trx_id" in resp

        resp = client.group.send_note(group_id, content="", image=[], inreplyto=trx_id)
        assert "trx_id" not in resp

        resp = client.group.like(group_id, trx_id)
        assert "trx_id" in resp

        resp = client.group.dislike(group_id, trx_id)
        assert "trx_id" in resp

        trxs = client.group.content(group_id)
        try:
            trxtype = client.trx.trx_type(trxs[-1])
            assert type(trxtype) == str
        except IndexError as e:
            print(e)
            pass

        r = client.group.send_img(group_id, "D:\\test-sample.png")
        assert "trx_id" in r

        r = client.node.create_group("测试一下下")
        assert "group_id" in r

        data = {"group_name": "nihao3", "app_key": "group_note"}
        r = client.node.create_group(**data)
        assert "group_id" in r

        r = client.group.create(**{"group_name": "nihao3", "app_key": "group_note"})
        assert "group_id" in r

        resp = client.group.leave(group_id)
        r2 = client.node.is_joined(group_id)
        assert r2 == False

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
        r = client.node.is_seed(seed)
        r = client.node.join_group(seed)

    def test_reformat(self):
        from officepy import Dir

        Dir(Config.BASE_DIR).black()


if __name__ == "__main__":
    pass
