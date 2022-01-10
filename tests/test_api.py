# -*- coding: utf-8 -*-

from datetime import datetime
import pytest
import sys

sys.path.append(r"D:\Jupyter\rum-py")

from rumpy import RumClient, WhoSays


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
        r = client.group.create("nihao")
        client.group.join(r)


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

    def test_trx(self):
        group_id = "bf005ff2-291e-4d4f-859d-fa5ba3e1c747"
        trxs = client.group.content(group_id)
        for trxdata in trxs[:50]:
            print(client.trx.trx_type(trxdata))

    def test_whosays(self):
        # 构建人物
        names_info = {
            "3bb7a3be-d145-44af-94cf-e64b992ff8f0": [
                "CAISIQODbcx2zjXC6AVGFNk3rzfoydQrIfXUu5FDD092fICQLA=="
            ],
            "bd119dd3-081b-4db6-9d9b-e19e3d6b387e": [
                "CAISIQN88AYbpppS6WuaYCE0/2OX+QSzq6IYgigwAodETppmGQ=="
            ],
        }
        # 对 huoju 的称呼
        name = "Huoju"
        # 本地数据文件，用来标记哪些动态已转发
        filepath = r"D:\Jupyter\my_auto_task\data\huoju_says_new.json"
        # 测试用，如果你也尝试，改为自己创建的组
        toshare_group_id = "f534c07c-4539-4739-8af6-6c0ded140d11"

        WhoSays(**kwgs).do(filepath, name, names_info, toshare_group_id)


TestGroup().test_whosays()
