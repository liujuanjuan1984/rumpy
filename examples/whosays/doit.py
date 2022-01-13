# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.realpath("."))
from whosays import WhoSays
from rumpy import JsonFile
from examples.config import client_params


def main():

    names_info = {
        "3bb7a3be-d145-44af-94cf-e64b992ff8f0": [
            "CAISIQODbcx2zjXC6AVGFNk3rzfoydQrIfXUu5FDD092fICQLA=="
        ],
        "bd119dd3-081b-4db6-9d9b-e19e3d6b387e": [
            "CAISIQN88AYbpppS6WuaYCE0/2OX+QSzq6IYgigwAodETppmGQ=="
        ],
    }
    name = "Huoju"
    filepath = r"D:\Jupyter\rumpy\examples\whosays\huoju_says.json"

    client = WhoSays(**client_params)

    data = JsonFile(filepath).read()

    data = client.search(names_info, data)
    JsonFile(filepath).write(data)

    group_id = client.group.create("测试whosays")["group_id"]
    data = client.send(name, group_id, data)
    JsonFile(filepath).write(data)


if __name__ == "__main__":
    main()
