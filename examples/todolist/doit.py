import os
import sys
from rumpyconfig import RumpyConfig
from todolist import ToDoList
from officepy import JsonFile


def main():
    client = ToDoList(**RumpyConfig.GUI)
    group_id = "5d53968c-3b48-44c5-953f-0abe0b7ad73d"
    pubkeys = [
        "CAISIQMsljkyD50GsX4uEARMKIql0FmxGgZY4A19wlSDyzRweg==",
        "CAISIQNKNsvS2jHrqPqQZoHfShqu9P7a81glEa/A2WUVFtwRBQ==",
        "CAISIQNK024r4gdSjIK3HoQlPbmIhDNqElIoL/6nQiYFv3rTtw==",
        "CAISIQN1KMgurpNaZr7xHMOzKJ2taJS2uYUgAxBQqv5KJmhaLw==",
        "CAISIQPlSoPo7GaXJq9iFV+TuSUKsBEyCYRCLO3vpZrb6HiiZA==",
    ]
    # 所有的 todolist 数据
    data = client.data(group_id, pubkeys)
    all_pd, todo_pd = client.todo_pd(group_id, pubkeys)
    print(todo_pd.head())


if __name__ == "__main__":
    main()
