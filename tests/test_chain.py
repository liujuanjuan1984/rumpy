import datetime
import logging

import pytest

now = datetime.datetime.now()

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    filename=f"tests_chain_{datetime.date.today()}_{now.hour}_{now.minute}.log",
    level=logging.WARNING,
)

from tests import client, group_names_to_leave

logger = logging.getLogger(__name__)


class TestChain:
    def __init__(self, client=None, group_id=None):
        self.client = client
        self._group_id = group_id
        self.main_test()

    def main_test(self):
        if self._group_id == None:
            for group_id in self.client.node.groups_id:
                self.client.group_id = group_id
                self.info = self.client.group.info().__dict__
                self.highest_block_id = self.info.get("highest_block_id")
                self.highest_height = self.info.get("highest_height")
                self._main_test()
        else:
            self.client.group_id = self._group_id
            self.info = self.client.group.info().__dict__
            self.highest_block_id = self.info.get("highest_block_id")
            self.highest_height = self.info.get("highest_height")
            self._main_test()

    def _main_test(self):
        logger.warning("+" * 33)
        logger.warning(f"group_id: <{self.client.group_id}>" + ", begin...")

        a = self.check_highest_height()
        b = self.check_block_back_to_genisis()
        c = self.check_decryp_trxs()
        d = self.check_prev_blocks()
        e = self.check_block_without_trx()
        f = self.check_trx_in_blocks()
        logger.warning(f"group_id: <{self.client.group_id}>" + ", results:")
        logger.warning(f"{a} check_highest_height ")
        logger.warning(f"{b} check_block_back_to_genisis")
        logger.warning(f"{c} check_decryp_trxs")
        logger.warning(f"{d} check_prev_blocks")
        logger.warning(f"{e} check_block_without_trx")
        logger.warning(f"{f} check_trx_in_blocks")
        logger.warning(f"group_id: <{self.client.group_id}>" + ", done.")

    def check_highest_height(self):
        """检查 groupchain 的 highest_height，是否和 nounce 一致？"""
        now_height = self.info.get("highest_height", 0)
        nouce_height = self.info.get("snapshot_info", {}).get("HighestHeight", 0)
        if now_height != nouce_height:
            logger.warning(f"highest_height is different. chain: {now_height}, snapshot: {nouce_height}")
            return False
        return True

    def check_block_back_to_genisis(self):
        """检查 groupchain 是否能从最高 block_id 回溯到初始 block"""

        bid = self.highest_block_id
        seed = self.client.group.seed()
        gensis_bid = seed["genesis_block"]["BlockId"]

        while bid:
            _pbid = self.client.group.block(bid).get("PrevBlockId", "")
            if _pbid == "":
                if bid != gensis_bid:
                    logger.warning(bid, "is not genesis block. and have no prev block")
                    return False
                return True
            bid = _pbid

    def check_decryp_trxs(self):
        """从区块头开始检查，是否所有数据都能解密"""
        bid = self.highest_block_id
        h = self.highest_height
        rlt = True
        while h > 0 and bid:
            block = self.client.group.block(bid)
            for trx in block.get("Trxs", {}):
                _trx = self.client.group.trx(trx["TrxId"])
                if "Content" not in _trx:
                    _trx_type = _trx.get("Type", "???")
                    if _trx_type not in [
                        "ASK_PEERID",
                        "ANNOUNCE",
                        "CHAIN_CONFIG",
                        "APP_CONFIG",
                        "USER",
                        "PRODUCER",
                    ]:
                        logger.warning(f"undecryption, height:{h},trx_id: {trx['TrxId']}, type: {_trx_type}")
                        rlt = False
            bid = block.get("PrevBlockId", "")
            h = h - 1
        return rlt

    def check_prev_blocks(self):
        """检查 group 的每个 block 是否为多个 block 的 prev block；从最高 block_id 往前回溯"""
        bid = self.highest_block_id
        h = self.highest_height

        rlt = True

        blocks = {}
        while bid:
            block = self.client.group.block(bid)
            _pbid = block.get("PrevBlockId", "")
            if bid not in blocks:
                blocks[bid] = _pbid
            else:
                blocks[bid] += "," + _pbid
                logger.warning(f"same prev blocks, height:{h}, block_id:{bid} is prev of blocks: {blocks[bid]}")
                rlt = False
            h = h - 1
            bid = _pbid

        return rlt

    def check_block_without_trx(self):
        """检查是否存在空 blocks"""
        bid = self.highest_block_id
        h = self.highest_height
        rlt = True
        while h > 0 and bid:
            block = self.client.group.block(bid)
            trxs = block.get("Trxs", {})
            if len(trxs) == 0:
                logger.warning(f"empty block, height:{h}, block_id: {bid}")
                rlt = False
            bid = block.get("PrevBlockId", "")
            h = h - 1
        return rlt

    def check_trx_in_blocks(self):
        """检查是否有同一个 trx 被打包进不同的 blocks"""
        bid = self.highest_block_id

        trxs = {}
        while bid:
            block = self.client.group.block(bid)
            for trx in block.get("Trxs", {}):
                tid = trx["TrxId"]
                if tid not in trxs:
                    trxs[tid] = bid
                else:
                    trxs[tid] += "," + bid
            bid = block.get("PrevBlockId", "")

        rlt = True
        for tid in trxs:
            if len(trxs[tid]) > 36:
                logger.warning(f"trx in blocks, trx_id:{tid}, block_id: {trxs[tid]}")
                rlt = False
        return rlt


if __name__ == "__main__":
    # TestChain(client,group_id='4e784292-6a65-471e-9f80-e91202e3358c')
    TestChain(client)
