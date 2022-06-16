import datetime
import logging
import os

import rumpy.utils as utils

logger = logging.getLogger(__name__)


class ExportData:
    def __init__(self, rum_client):
        self.rum = rum_client

    # TODO:这个处理适合whosays借鉴？
    def data_generator(self, group_id, senders):
        trxs = self.rum.api.get_group_all_contents(group_id=group_id, senders=senders)
        nicknames = self.rum.api.get_profiles(group_id=group_id, types=("name",))
        for trx in trxs:
            params = self.rum.api.trx_retweet_params(group_id=group_id, trx=trx, nicknames=nicknames)
            params.update({"trx_id": trx["TrxId"]})
            yield params

    def save_to_dir(self, group_id, datadir, filetype="md", pubkeys=None):
        # check dir
        imgdir = os.path.join(datadir, "images")
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        if filetype not in ("md", "html"):
            filetype = "md"
            logger.warning(f"filetype {filetype} is not supported yet.")

        _today = datetime.date.today()
        textfilename = f"{_today}_Group_{group_id}.{filetype}"
        textfile = os.path.join(datadir, textfilename)

        senders = pubkeys or [self.rum.api.group_info(group_id).user_pubkey]
        data = self.data_generator(group_id, senders)
        hander = open(textfile, "w+", encoding="utf-8")
        title = {
            "html": f"""<!DOCTYPE html>\n<html lang="zh-CN">\n<head><h1>Export Data</h1>\n<p>Group: {group_id}</p><p>Senders: {senders}</p></head>\n<body>\n""",
            "md": "\n\n".join([f"# Group: {group_id}", f"Senders: {senders}"]),
        }
        hander.write(title[filetype])

        # write to html file.

        for params in data:
            # one trx start.
            _md = f"""<!-- group_id="{group_id}" trx_id="{params['trx_id']}-->\n\n"""
            text = {"html": f"<div></div>\n<section>\n{_md}", "md": _md}
            hander.write(text[filetype])

            # content in trx
            if lines := params.get("content"):
                _lines = lines.split("\n")
                _html = "\n".join([f"<div>{i}</div>" for i in _lines]) + "\n<div></div>\n"
                _md = "\n\n".join(_lines) + "\n\n"
                text = {"html": _html, "md": _md}
                hander.write(text[filetype])

            # images in trx: write imgs to imgdir
            for img in params.get("images", []):
                imgb, _ = utils.get_filebytes(img["content"])
                imgname = img.get("name", utils.filename_init_from_bytes(imgb))
                imgname = utils.filename_check(imgname)  # 可能有不支持的特殊符号
                imgpath = os.path.join(imgdir, imgname)
                with open(imgpath, "wb") as f:
                    f.write(imgb)
                _html = f'\n<img src="images/{imgname}"></img>\n'
                _md = "\n\n".join([f"![](images/{imgname})", "------"]) + "\n\n"
                imgquote = {"html": _html, "md": _md}
                hander.write(imgquote[filetype])

            # one trx end.
            text = {"html": f"</section>\n<hr>\n", "md": "----\n\n"}
            hander.write(text[filetype])

        text = {"html": "</body>\n</html>", "md": "\n<!--end-->\n\n"}
        hander.write(text[filetype])
        hander.close()


if __name__ == "__main__":
    from rumpy import FullNode

    client = FullNode()
    bot = ExportData(client)
    datadir = r"D:\export_data_test"
    group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
    # bot.save_to_dir(group_id, datadir, "md")
    bot.save_to_dir(group_id, datadir, "html")  # TODO:直接这样写html不太好，没有对文本做转义，比如js代码会被执行。
