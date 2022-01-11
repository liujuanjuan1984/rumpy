import os
import json
from datetime import datetime


class JsonFile:
    """.json 数据文件"""

    def __init__(self, filepath):
        self.filepath = filepath

    def read(self, nulldata={}):
        """读取 json 文件，nulldata 可以指定文件不存在时返回的数据"""
        if not os.path.exists(self.filepath):
            return nulldata
        try:
            with open(self.filepath, "r", encoding="utf-8") as __f:
                filedata = json.load(__f)
            return filedata
        except Exception as e:
            print(e)
            print(datetime.now(), self.filepath, "failed，not json file")
            return nulldata

    def write(self, filedata, indent=1, is_print=True, is_cover=True):
        """把数据写入 json 文件，indent 默认指定缩进值为 1"""
        # 文件已存在，且不想覆盖时，就自动生成 temp
        filepath = self.filepath
        if os.path.exists(self.filepath) and is_cover == False:
            filepath += str(datetime.now())[-6:] + ".temp.json"

        with open(filepath, "w", encoding="utf-8") as __f:
            try:
                json.dump(
                    filedata, __f, indent=indent, sort_keys=False, ensure_ascii=False
                )
            except Exception as e:
                print(e)
                json.dump(
                    filedata,
                    __f,
                    indent=indent,
                    sort_keys=False,
                    ensure_ascii=False,
                    cls=MyEncoder,
                )
        if is_print:
            print(datetime.now(), filepath, f"write_file_by_json done.")

    def rewrite(self):
        """重新读写数据文件，通常是为了规范格式，以方便检查改动"""
        data = self.read_file_by_json()
        self.write_file_by_json(data)
