from config import Config
from officepy import JsonFile
from search_user import SearchUser


searchuser = SearchUser(**Config.CLIENT_PARAMS["gui"])

for xname in ["xiaolai", "huoju"]:
    rlt = searchuser.innode(xname)
    JsonFile(f"examples/search_user/data/search_user_{xname}.json").write(rlt)
