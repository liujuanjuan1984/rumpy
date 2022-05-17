import datetime
import sys

sys.path.insert(0, r"D:\Jupyter\rumpy")
from rumpy.utils import ts2datetime
from tests import client

seed = client.group.create("mytest_pubqueque")
client.group_id = seed["group_id"]


def test_basic():
    r = client.group.pubqueue()
    print(r)


def test_update():
    for i in range(10):
        client.group.send_note(content=f"{str(i)*10}")

    data = client.group.pubqueue()
    print(data)

    for idata in data:
        s1 = ts2datetime(idata["UpdateAt"])
        s2 = ts2datetime(idata["Trx"]["TimeStamp"])
        s3 = ts2datetime(idata["Trx"]["Expired"])
        s4 = datetime.datetime.now()
        tid = idata["Trx"]["TrxId"]
        print(idata["State"], tid, s2, s1 - s2)


def test_end():
    client.group.leave()


if __name__ == "__main__":
    test_basic()
    test_update()
    # test_end()
