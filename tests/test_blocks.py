import pytest
import os
from officepy import JsonFile, Stime
from rumpyconfig import RumpyConfig
from rumpy import RumClient

client = RumClient(**RumpyConfig.GUI)


def test_blocks(gid, fromfile, tofile):
    """get all blocks of a group chain."""
    bids = []
    bid = client.group.info(gid).highest_block_id

    if fromfile:
        bids = JsonFile(fromfile).read([])
        if len(bids) >= 1:
            bid = bids[0]

    while True:
        if bid in bids:
            print("info:", gid, bid, "exists!!!")
            break
        else:
            bids.append(bid)

        block = client.group.block(gid, bid)
        if block:
            bid = block.get("PrevBlockId")
        else:
            print(block)
            break
        if not bid:
            break
    if tofile:
        JsonFile(tofile).write(bids)

    print(gid, "blocks num:", len(bids))


def test_trxs_in_blocks(gid, fromfile, tofile):
    """get all blocks of a group chain."""

    if fromfile:
        tids = JsonFile(fromfile).read({})
    else:
        tids = {}

    bid = client.group.info(gid).highest_block_id
    flag = True
    while flag:
        block = client.group.block(gid, bid)
        if block:
            trxs = block.get("Trxs") or []
            for trx in trxs:
                tid = trx["TrxId"]
                if tid not in tids:
                    tids[tid] = [bid]
                elif bid not in tids[tid]:
                    tids[tid].append(bid)
                else:
                    flag = False
                    break

            bid = block.get("PrevBlockId")
        else:
            print(block)
            break

        if not bid:
            break

    if tofile:
        JsonFile(tofile).write(tids)

    print(gid, "trxs num:", len(tids))


if __name__ == "__main__":
    gid = RumpyConfig.GROUPS["去中心微博"]
    gid = RumpyConfig.GROUPS["刘娟娟的朋友圈"]
    gids = [
        "b280446c-3562-4277-b14e-be7a15bb4718",
        "fed57711-8aed-4944-bf9b-d15420d17f4b",
        "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436",
    ]
    for gid in gids:
        this_dir = os.path.dirname(__file__)

        blocksfile = os.path.join(this_dir, "data", f"{gid}_blocks.json")
        trxsfile = os.path.join(this_dir, "data", f"{gid}_trxs.json")

        test_blocks(gid, blocksfile, blocksfile)
        test_trxs_in_blocks(gid, trxsfile, trxsfile)

        trxs = JsonFile(trxsfile).read()
        for tid in trxs:
            if len(trxs[tid]) > 1:
                day = Stime.ts2datetime(client.group.trx(gid, tid)["TimeStamp"])
                if f"{day}" >= "2022-02-20":
                    print(tid, len(trxs[tid]), day)
