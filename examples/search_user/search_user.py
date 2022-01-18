# -*- coding: utf-8 -*-


import os
import sys


sys.path.append(os.path.realpath("."))
from rumpy import JsonFile, RumClient
from examples.config import client_params


client = RumClient(**client_params)

for xname in ["xiaolai", "huoju"]:
    rlt = client.node.search_user(xname)
    JsonFile(f"examples/search_user/data/search_user_{xname}.json").write(rlt)
