import json
import logging
import re
from typing import Dict, List

import rumpy.utils as utils

logger = logging.getLogger(__name__)


class SearchSeeds:
    def __init__(self, rum_client):
        self.rum = rum_client

    def search_in_text(self, text: str) -> List:
        """
        Search seeds in text, return list of seeds.
        Only one seed in text can be found.
        """
        seeds = []
        pttn = r"""({['"].*genesis_block.*['"]})"""
        for i in re.findall(pttn, text or "", re.S):
            try:
                iseed = json.loads(i)
                if utils.is_seed(iseed):
                    seeds.append(iseed)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.warning(e)
                continue
        return seeds

    def search_in_trx(self, trx: Dict) -> List:
        """Search seeds in trx, return list of seeds."""
        seeds = []
        if text := trx["Content"].get("content"):
            seeds = self.search_in_text(text)
        return seeds

    def search_in_group(self, group_id, trx_id=None, seeds=None):
        seeds = seeds or {}
        if group_id not in seeds:
            if seed := self.rum.api.seed(group_id):
                seeds[group_id] = seed

        trxs = self.rum.api.get_group_all_contents(
            group_id=group_id,
            trx_id=trx_id,
            trx_types=("text_only", "image_text", "reply"),
        )
        progress_tid = trx_id
        for trx in trxs:
            progress_tid = trx["TrxId"]
            if _seeds := self.search_in_trx(trx):
                for seed in _seeds:
                    gid = seed["group_id"]
                    if gid not in seeds:
                        seeds[gid] = seed
        return progress_tid, seeds

    def search_in_node(self, progress=None, seeds=None):
        progress = progress or {}
        seeds = seeds or {}

        for group_id in self.rum.api.groups_id:
            trx_id = progress.get(group_id)
            progress_tid, seeds = self.search_in_group(group_id, trx_id, seeds)
            progress[group_id] = progress_tid
        return progress, seeds

    def io_with_file(self, data_dir=None):
        import os

        from officy import JsonFile

        data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        progress_file = os.path.join(data_dir, f"search_seeds_progress.json")
        rlt_file = os.path.join(data_dir, f"search_seeds_rlt.json")
        progress = JsonFile(progress_file).read({})
        rlt = JsonFile(rlt_file).read({})
        progress, rlt = self.search_in_node(progress, rlt)
        JsonFile(progress_file).write(progress)
        JsonFile(rlt_file).write(rlt)

    def io_with_db(self):  # TODO:
        pass


if __name__ == "__main__":
    from rumpy import FullNode

    rum = FullNode()
    SearchSeeds(rum).io_with_file(data_dir=r"D:\Jupyter\seeds\data")
