import os
from typing import List, Dict


class Dir:
    """文件夹"""

    def __init__(self, dirpath):
        self.dirpath = dirpath

    def check_dir(self):
        """检查文件夹是否存在；如果不存在则创建文件夹，可以逐层创建"""
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)

    def search_files_by_types(self, filetypes) -> List:
        """搜索文件夹中指定类型的文件，返回文件的绝对路径构成的列表"""
        filepaths = []
        for roots, dirnames, filenames in os.walk(self.dirpath):
            for ifile in filenames:
                if ifile.endswith(filetypes):
                    xfile = os.path.join(roots, ifile)
                    filepaths.append(xfile)
        return filepaths

    def black_auto(self):
        """采用 black 自动对本目录所有源文件处理为 PEP8 规范"""

        for i in self.search_files_by_types(".py"):
            line = f"black {i}"
            os.system(line)
