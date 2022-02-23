import os
import sys
from rumpyconfig import RumpyConfig
from search_seeds import SearchSeeds
from officepy import JsonFile, Dir


def main():
    # 初始化
    client = SearchSeeds(**RumpyConfig.GUI)
    # 数据文件
    dirpath = f"{os.path.realpath('.')}\\examples\\search_seeds\\data"
    Dir(dirpath).check()
    filepath = f"{dirpath}\\search_seeds_and_joined_data.json"
    data = JsonFile(filepath).read()

    # 搜寻种子并更新数据文件
    data = client.search_seeds(data)
    JsonFile(filepath).write(data)

    # 离开某些种子网络，比如大量测试用种子
    # is_block 为真，表示离开区块数为 0 的种子网络；为否表示不离开
    # 离开过的种子网络会自动标记不值得加入，避免以后重复加入
    toleave_groupnames = [
        "测试hellorum",
        "测试whosays",
        "测试种子大全",
        "新增测试组",
        "nihao",
        "nihao3",
        "测试一下",
        "测试一下下",
    ]

    data = client.leave_group(data, toleave_groupnames, is_block=True)
    JsonFile(filepath).write(data)

    # 加入未曾加入的种子网络
    data = client.group.join(data)
    JsonFile(filepath).write(data)

    # 分享到种子网络
    group_id = "8ed3b4ce-c151-4942-9059-2a2cc7952ad2"  # 测试用
    data = client.share(data, group_id)
    JsonFile(filepath).write(data)


if __name__ == "__main__":
    main()
