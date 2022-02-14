import os
import json
import datetime


class JsonFile:
    """.json 数据文件"""

    def __init__(self, filepath):
        self.filepath = filepath

    def read(self, nulldata={}):
        """读取 json 文件，nulldata 可以指定文件不存在时返回的数据"""
        if not os.path.exists(self.filepath):
            return nulldata
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                filedata = json.load(f)
            return filedata
        except:
            return nulldata

    def write(self, filedata, indent=1, is_cover=True):
        """把数据写入 json 文件，indent 默认指定缩进值为 1"""
        # 文件已存在，且不想覆盖时，就自动生成 temp
        filepath = self.filepath
        if os.path.exists(filepath) and not is_cover:
            filepath += f"{datetime.date.today()}.temp.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(filedata, f, indent=indent, sort_keys=False, ensure_ascii=False)

    def rewrite(self):
        """重新读写数据文件，通常是为了规范格式，以方便检查改动"""
        self.write(self.read())
