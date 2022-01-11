# -*- coding: utf-8 -*-

"""use `black` to reformat the python files. need to install `black` first."""

import os

for root, paths, names in os.walk("./"):
    for name in names:
        if name.endswith(".py"):
            ifile = root + "\\" + name
            os.system(f"black {ifile}")
