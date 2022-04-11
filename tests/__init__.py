from rumpy import RumClient

group_names_to_leave = []
keys = {
    "port": 58356,
    "crtfile": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
}

client = RumClient(**keys)
