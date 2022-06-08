import datetime
import os
import sys

from officy import Dir, JsonFile
from search_seeds import SearchSeeds


def main():
    # init client
    print(datetime.datetime.now(), "client init...")
    client = SearchSeeds()

    # datafiles
    print(datetime.datetime.now(), "datafiles...")
    basedir = os.path.join(os.path.dirname(__file__), "data")
    datafiles = {
        "seedsfile": r"D:\Jupyter\seeds\data\seeds.json",
        "progressfile": os.path.join(basedir, "progressfile.json"),
        "infofile": r"D:\Jupyter\seeds\data\groupsinfo.json",
    }
    client.init_app(**datafiles)

    # search seeds
    print(datetime.datetime.now(), "search seeds in node...")
    client.innode()

    # leave groups
    print(datetime.datetime.now(), "leave usless groups...")
    client.leave_groups()

    # join groups
    # print(datetime.datetime.now(), "join  groups...")
    # client.join_groups()

    # update status
    print(datetime.datetime.now(), "update status...")
    client.update_status()


if __name__ == "__main__":
    main()
