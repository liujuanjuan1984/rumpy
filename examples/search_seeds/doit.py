import datetime
import os
import sys
from rumpyconfig import RumpyConfig
from search_seeds import SearchSeeds
from officepy import JsonFile, Dir


def main():
    # init client
    print(datetime.datetime.now(), "client init...")
    client = SearchSeeds(**RumpyConfig.GUI)

    # datafiles
    print(datetime.datetime.now(), "datafiles...")
    basedir = os.path.join(os.path.dirname(__file__), "data")
    datafiles = {
        "datafile": os.path.join(basedir, "datafile.json"),
        "logfile": os.path.join(basedir, "logfile.json"),
        "trxfile": os.path.join(basedir, "trxfile.json"),
        "infofile": os.path.join(basedir, "infofile.json"),
    }
    client.init_app(**datafiles)

    # search seeds
    print(datetime.datetime.now(), "search seeds in node...")
    client.innode()

    # leave groups
    print(datetime.datetime.now(), "leave usless groups...")
    client.leave_groups()

    # join groups
    print(datetime.datetime.now(), "join  groups...")
    client.join_groups()


if __name__ == "__main__":
    main()
