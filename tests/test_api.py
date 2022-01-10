# -*- coding: utf-8 -*-

from datetime import datetime
import pytest
import sys

sys.path.append(r"D:\Jupyter\rum-py")

from rumpy import RumClient


kwgs = {
    "appid": "my-live-rum-app",
    "host": "127.0.0.1",
    "port": 55043,
    "cacert": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
}

client = RumClient(**kwgs)


class TestNode(object):
    def test_node(self):
        client.node.info()
        client.node.status
        client.node.id
        client.node.pubkey

    def test_node_network(self):
        client.node.network

    def test_node_groups(self):
        client.node.groups()
        r = client.node.groups_id

    def test_node_is_joined(self):
        group_id = "5d53968c-3b48-44c5-953f-0abe0b7ad73d"
        r1 = client.node.is_joined(group_id)
        assert r1 == True
        group_id = "5d53968c-3b48-44c5-953f-0abe0b7ad73e"
        r2 = client.node.is_joined(group_id)
        assert r2 == False

    def test_group_create(self):
        r = client.node.create_group("新增测试组")
        assert "genesis_block" in r
        client.node.join_group(r)


class TestGroup(object):
    def test_content(self):
        # 种子
        group_id = "bf005ff2-291e-4d4f-859d-fa5ba3e1c747"
        client.group.seed(group_id)

        # 发文
        resp = client.group.send_note(group_id, "你好")
        # client.group.send_note(group_id, "",[])
        client.group.send_note(group_id, imgs=["D:\\test-sample.png"])
        # 回复
        trx_id = resp["trx_id"]
        client.group.send_note(group_id, "我回复你了", [], trx_id)
        # client.group.send_note(group_id, "",[],trx_id)
        client.group.send_note(group_id, imgs=[], trx_id=trx_id)
        client.group.like(group_id, trx_id)
        client.group.dislike(group_id, trx_id)
