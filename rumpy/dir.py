import os
from typing import List, Dict


class Dir:
    """文件夹"""

    def __init__(self, dirpath):
        self.dirpath = dirpath.replace("/", "\\")

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
                    xfile = f"{roots}\\{ifile}"
                    filepaths.append(xfile)
        return filepaths

    def search_files_by_names(self, names: List) -> List:
        """搜索指定文件夹中名字含有某些词片段的文件，返回文件的绝对路径构成的列表；可指定多个片段"""
        filepaths = []
        for roots, dirnames, filenames in os.walk(self.dirpath):
            for ifile in filenames:
                for iname in names:
                    if ifile.find(iname) >= 0:
                        xfile = f"{roots}\\{ifile}"
                        filepaths.append(xfile)
                        break
        return filepaths

    def move_dirs(self, afdir):
        """把 dirpath 作为一个整体，不改名，移动到 afdir 目录之下"""
        dirname = self.dirpath.split("\\")[-1]
        at = f"{afdir}\\{dirname}"
        if os.path.exists(at):
            return print(at, "已存在该文件夹，改名自动取消")
        self.check_dir(afdir)
        os.rename(self.dirpath, at)

    def black_auto(self):
        """采用 black 自动对本目录所有源文件处理为 PEP8 规范"""

        for i in self.search_files_by_types(".py"):
            line = f"black.exe {i}"
            os.system(line)
