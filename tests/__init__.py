import sys

sys.path.insert(0, r"D:\Jupyter\rumpy")
from rumpy import RumClient

group_names_to_leave = []
keys = {"port": 58356}

client = RumClient(**keys)
