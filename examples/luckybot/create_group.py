# 初始化
import json
from config import *
from rumpy import RumClient

rum = RumClient(port=rum_port)

# 创建种子网络
seed = rum.group.create("每天的小确幸")
# 把种子分享到 刘娟娟的朋友圈（或其它地方，以吸引更多人加入）
rum.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
rum.group.send_note(content=json.dumps(seed))

# 初始化种子网络的权限
rum.group_id = seed["group_id"]
print(rum.config.set_trx_mode("REQ_BLOCK_FORWARD", "alw"))
print(rum.config.set_trx_mode("REQ_BLOCK_BACKWARD", "alw"))
print(rum.config.set_trx_mode("POST", "alw"))

# 把 owner 自己加入白名单
print(rum.config.update_allow_list(rum.group.pubkey, "hi", ["REQ_BLOCK_FORWARD", "REQ_BLOCK_BACKWARD", "POST"]))

# 查看表名单
print(rum.config.allow_list)
