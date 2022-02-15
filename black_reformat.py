# -*- coding: utf-8 -*-

"""use `black` to reformat the python files. need to install `black` first."""

import os
from officepy.officepy import Dir, JsonFile

# 对 .py 采用 black 重写
Dir("./").black()

# 对 .json 重写
# for i in Dir("./").search_files_by_types(".json"):
#    JsonFile(i).rewrite()
