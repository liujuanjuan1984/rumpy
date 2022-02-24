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

    CLIENT_PARAMS = {
        "gui": {
            "host": "127.0.0.1",
            "port": 50415,
            "appid": "peer",
            "crtfile": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
            "dbname": "gui_db",
        },
        "cli": {
            "host": "127.0.0.1",
            "port": 50415,
            "appid": "peer",
            "crtfile": r"D:\RUM2-DATA\certs\server.crt",
            "dbname": "cli_db",
        },
        "test": {
            "host": "127.0.0.1",
            "port": 50125,
            "appid": "peer",
            "crtfile": r"D:\RUM2-DATA\certs\server.crt",
            "dbname": "test_db",
        },
    }

    GUI = CLIENT_PARAMS["gui"]
    CLI = CLIENT_PARAMS["cli"]
    TEST = CLIENT_PARAMS["test"]
