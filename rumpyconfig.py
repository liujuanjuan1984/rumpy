import os


class RumpyConfig:
    RUMPY_BASEDIR = os.path.dirname(__file__)
    GROUPS = {
        "去中心微博": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "刘娟娟的朋友圈": "4e784292-6a65-471e-9f80-e91202e3358c",
    }

    # the group_name of groups that you want to leave

    TEST_GROUPS_TO_LEAVE = [
        "mytest_group",
    ]

    NAME_PIECES_TO_LEAVE = ("mytest", "测试", "test")

    # https://github.com/liujuanjuan1984/seeds/blob/master/data/seeds.json
    SEEDSFILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "seeds", "data", "seeds.json"
    )
    CLIENT_PARAMS = {
        "gui": {
            "host": "127.0.0.1",
            "port": 55882,
            "appid": "peer",
            "crtfile": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
            "usedb": False,
            "dbname": "gui_db",
            "dbecho": True,
            "dbreset": True,
        },
        "cli": {
            "host": "127.0.0.1",
            "port": 55882,
            "appid": "peer",
            "crtfile": r"D:\RUM2-DATA\certs\server.crt",
            "usedb": False,
            "dbname": "cli_db",
            "dbecho": True,
            "dbreset": True,
        },
        "test": {
            "host": "127.0.0.1",
            "port": 50125,
            "appid": "peer",
            "crtfile": r"D:\RUM2-DATA\certs\server.crt",
            "usedb": True,
            "dbname": "test_db",
            "dbecho": True,
            "dbreset": True,
        },
        "cloud": {
            "host": "127.0.0.1",
            "port": 62663,
            "appid": "peer",
            "crtfile": r"C:\certs\server.crt",
            "usedb": False,
            "dbname": "test_db",
            "dbecho": True,
            "dbreset": True,
        },
    }

    GUI = CLIENT_PARAMS["gui"]
    CLI = CLIENT_PARAMS["cli"]
    TEST = CLIENT_PARAMS["test"]
