import os


class Config:
    BASE_DIR = os.path.dirname(__file__)
    GROUPS = {
        "去中心微博": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "刘娟娟的朋友圈": "4e784292-6a65-471e-9f80-e91202e3358c",
    }

    TEST_GROUPS_TO_LEAVE = [
        "hellorum",
        "测试whosays",
        "新增测试组",
        "nihao",
        "nihao3",
        "测试一下",
        "测试一下下",
    ]

    CLIENT_PARAMS = {
        "gui": {
            "port": "127.0.0.1",
            "host": 50415,
            "appid": "peer",
            "crtfile": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
        },
        "cli": {
            "port": "127.0.0.1",
            "host": 50415,
            "appid": "peer",
            "crtfile": r"D:\RUM2-DATA\certs\server.crt",
        },
    }
