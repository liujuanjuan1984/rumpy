from config import RumpyConfig
from officepy import JsonFile
from search_user import SearchUser


searchuser = SearchUser(**RumpyConfig.CLIENT_PARAMS["gui"])

for xname in ["xiaolai", "huoju"]:
    rlt = searchuser.innode(xname)
    JsonFile(f"examples/search_user/data/search_user_{xname}.json").write(rlt)
