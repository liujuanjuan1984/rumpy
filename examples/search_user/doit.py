from rumpyconfig import RumpyConfig
from officepy import JsonFile
from search_user import SearchUser


searchuser = SearchUser(**RumpyConfig.GUI)

for xname in ["xiaolai", "huoju"]:
    rlt = searchuser.innode(xname)
    JsonFile(f"examples/search_user/data/search_user_{xname}.json").write(rlt)
