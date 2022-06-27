import sys

sys.path.insert(0, r"D:\Jupyter\rumpy")
from rumpy import LightNode

urls = ["https://127.0.0.1:51194"]

from rumpy import FullNode, LightNode

full = FullNode()
light = LightNode()

assert type(full.api.groups()) == list
assert type(light.api.groups()) == list

assert type(full.api.groups_id) == list
assert type(light.api.groups_id) == list
