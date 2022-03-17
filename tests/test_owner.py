import pytest
import os
import datetime
import json
from officepy import JsonFile, Dir, File, Stime
from rumpyconfig import RumpyConfig
from rumpy import RumClient

client = RumClient(**RumpyConfig.GUI)


def test_owner():
    owners = []
    users = []
    for gid in client.node.groups_id:
        client.group_id = gid
        if client.group.is_owner():
            owners.append(" ".join(["owner:", gid, client.group.info().group_name]))
        else:
            users.append(" ".join(["user:", gid, client.group.info().group_name]))
    print("=====You are in these groups:=====")
    print("+" * 66)
    print(*owners, sep="\n")
    print("+" * 66)
    print(*users, sep="\n")


def test_abandoned():
    seedsfile = RumpyConfig.SEEDSFILE
    infofile = seedsfile.replace("seeds.json", "groupsinfo.json")
    seeds = JsonFile(seedsfile).read()
    info = JsonFile(infofile).read()
    print("=====You are in these abandoned groups:=====")
    for gid in client.node.groups_id:
        if gid in info:
            if info[gid].get("abandoned"):
                print(gid, seeds[gid]["group_name"])


if __name__ == "__main__":
    test_owner()
    test_abandoned()
