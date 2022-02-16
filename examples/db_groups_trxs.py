import sqlite3
import datetime
import pytest
import os
import sys
import json


from rumpy import RumClient
from config import Config


def tables():
    # 查询已有的 tables
    data = cu.execute(f"""SELECT name from sqlite_master where type='table'""")
    con.commit()
    tables = [i[0] for i in data]
    return tables


def table_node_groups():

    # 创建表格
    if "node_groups" not in tables():
        sql_create_table = """CREATE TABLE node_groups (
        group_id varchar(64) UNIQUE,
        group_name varchar(128) ,
        owner_pubkey varchar(128)  ,
        user_pubkey varchar(128)  ,
        consensus_type  varchar(20)  ,
        encryption_type varchar(20)  ,
        cipher_key varchar(128)  , 
        app_key varchar(64)  , 
        last_updated timestamp ,
        highest_height int,
        highest_block_id  varchar(128) ,
        group_status varchar(128))"""

        cu.execute(sql_create_table)
        con.commit()
        print("表格创建成功")

    groups = client.node.groups()

    for g in groups:
        # 插入数据
        try:
            cu.execute(
                "INSERT INTO node_groups VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                tuple(g.values()),
            )
            con.commit()
        # 更新数据
        except Exception as e:
            sql = f"""UPDATE node_groups 
            set last_updated=  {g['last_updated']},
            highest_height =  {g['highest_height']},
            highest_block_id = '{g['highest_block_id']}',
            group_status = '{g['group_status']}'
            where group_id='{g['group_id']}'"""
            cu.execute(sql)
            con.commit()
        finally:
            pass

    data = cu.execute("SELECT group_id,group_name,last_updated from node_groups")
    con.commit()
    groups = [
        (group_id, group_name, last_updated)
        for (group_id, group_name, last_updated) in data
    ]
    return groups


def group_id_to_table_name(group_id):
    return "gc_" + group_id.replace("-", "_")


def table_name_to_group_id(table_name):
    return table_name[3:].replace("_", "-")


def table_group_trxs(group_id):
    gt_name = group_id_to_table_name(group_id)

    # 创建表格
    if gt_name not in tables():
        sql = f"""CREATE TABLE {gt_name} (TrxId varchar(20) UNIQUE,Publisher varchar(128) ,Content text  ,TypeUrl varchar(64)  ,TimeStamp  int )"""
        cu.execute(sql)
        con.commit()

    # 查询内容并写入数据库

    # 从数据库中查找
    data = cu.execute(f"""SELECT TrxId from {gt_name} order by TimeStamp limit 0,1""")
    con.commit()
    trx_id = [TrxId for (TrxId,) in data][0] or "0"  # 查不到就默认为 0

    trxs = client.group.content_trxs(group_id, trx_id)

    while len(trxs):
        for trx in trxs:
            trx["Content"] = json.dumps(trx["Content"])
            try:
                cu.execute(
                    f"INSERT INTO {gt_name} VALUES (?,?,?,?,?)", tuple(trx.values())
                )
                con.commit()
            except:
                pass

        # 该处理主要是避免陷入死循环，但同时又需要关注该种异常
        xtrx_id = trxs[-1]["TrxId"]
        if xtrx_id != trx_id:
            trx_id = xtrx_id
        else:
            print(group_id, trx_id, trxs)
            break
        print(datetime.datetime.now(), trx_id, "get content_trxs ...")

        trxs = client.group.content_trxs(group_id, trx_id)


def table_groups_trxs():
    groups = table_node_groups()
    for (group_id, _, _) in groups:
        print(datetime.datetime.now(), group_id, "...")
        table_group_trxs(group_id)
        print(datetime.datetime.now(), group_id, "done.")


if __name__ == "__main__":

    client = RumClient(**Config.CLIENT_PARAMS["gui"])

    # 采用 node 的 id 作为 db 的识别标记
    dbpath = homedir + f"\\database\\node_{client.node.id}.db"

    # 与已有数据库建立连接，没有就创建
    con = sqlite3.connect(dbpath)
    cu = con.cursor()

    table_node_groups()
    table_groups_trxs()

    con.close()
