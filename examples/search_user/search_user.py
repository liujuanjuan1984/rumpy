# -*- coding: utf-8 -*-


import os
import sys
from rumpy import RumClient
from officepy import JsonFile
from config import Config


client = RumClient(**Config.CLIENT_PARAMS["gui"])

for xname in ["xiaolai", "huoju"]:
    rlt = client.node.search_user(xname)
    JsonFile(f"examples/search_user/data/search_user_{xname}.json").write(rlt)
