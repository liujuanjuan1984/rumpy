import asyncio
import time
import os
from rumpy import RumClient
from officy import JsonFile, Stime
from xinbot import MixinBotApi
from rss_config import *

rum = RumClient(port=rum_port)

progress_file = os.path.join(os.path.dirname(__file__), "data", "progress.json")
progress = JsonFile(progress_file).read({})


async def run():
    xin = MixinBotApi(xin_config)
    for gid in rum_groups:
        rum.group_id = gid

        if not rum.group.is_joined():
            continue

        gname = rum_groups.get(gid) or rum.group.seed()["group_name"]
        print(gid, gname)

        if gid not in progress:
            _trxs = rum.group.content_trxs(is_reverse=True)
            if len(_trxs) > 0:
                trx_id = _trxs[-1]["TrxId"]
            else:
                trx_id = None
        else:
            trx_id = progress.get(gid)

        progress[gid] = trx_id
        JsonFile(progress_file).write(progress)

        trxs = rum.group.content_trxs(trx_id=trx_id)

        for trx in trxs:

            ts = Stime.ts2datetime(trx["TimeStamp"])
            if str(ts) <= "2022-05-04":
                continue

            try:
                text = trx["Content"]["content"]
            except:
                continue

            time.sleep(1)

            if text:
                data = f"{ts}@{gname}\n" + text.encode().decode("utf-8")
                print(data)
                await xin.send_text_message(conversation_id, data)

                progress[gid] = trx_id
                JsonFile(progress_file).write(progress)

            """ 
            elif rum.group.trx_type(trx) == "image_only":
                imgs = trx["Content"]['image']
                for img in imgs:
                    data = img['content']
                    await xin.send_img_message(conversation_id, data)
            """

    await xin.close()


asyncio.run(run())
