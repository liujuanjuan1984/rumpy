from rumpy import FullNode
from rumpy.bots import SearchUser

rum = FullNode()
SearchUser(rum, "huoju").io_with_file(data_dir=r"D:\Jupyter\rumpy\rum_whosays\whosays")
