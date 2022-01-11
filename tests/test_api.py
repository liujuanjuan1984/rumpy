# -*- coding: utf-8 -*-

from time import sleep
import pytest
import sys

sys.path.append(r"D:\Jupyter\rumpy")

from rumpy import RumClient

kwgs = {
    "appid": "peer",
    "host": "127.0.0.1",
    "port": 55043,
    "cacert": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
}

client = RumClient(**kwgs)


class TestCase(object):
    def test_api(self):

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
            kwargs = {"text": f"你好 {i}"}
            r5 = client.group.send_note(group_id, **kwargs)
            assert "trx_id" in r5

        trx_id = r5["trx_id"]
        kwargs = {"text": "回复一下", "trx_id": trx_id}
        r6 = client.group.send_note(group_id, **kwargs)
        assert "trx_id" in r6

        # 发文
        resp = client.group.send_note(group_id, "你好")
        assert "trx_id" in resp

        resp = client.group.send_note(group_id, "", [])
        assert "trx_id" not in resp

        resp = client.group.send_note(group_id, imgs=["D:\\test-sample.png"])
        assert "trx_id" in resp

        # 回复
        trx_id = resp["trx_id"]
        resp = client.group.send_note(group_id, "我回复你了", [], trx_id)
        assert "trx_id" in resp

        resp = client.group.send_note(group_id, "", [], trx_id)
        assert "trx_id" not in resp

        resp = client.group.send_note(group_id, imgs=[], trx_id=trx_id)
        assert "trx_id" not in resp

        for i in range(5):
            resp = client.group.like(group_id, trx_id)
            assert "trx_id" in resp

        for i in range(3):
            resp = client.group.dislike(group_id, trx_id)
            assert "trx_id" in resp

        trxs = client.group.content(group_id)
        for trxdata in trxs:
            trxtype = client.trx.trx_type(trxdata)
            assert type(trxtype) == str

        resp = client.group.leave(group_id)
        r2 = client.node.is_joined(group_id)
        assert r2 == False
