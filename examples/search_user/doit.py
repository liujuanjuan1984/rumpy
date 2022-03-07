import os
from rumpyconfig import RumpyConfig
from officepy import JsonFile
from search_user import SearchUser

searchuser = SearchUser(**RumpyConfig.GUI)

# example: one

searchuser.init("huoju")
searchuser.innode()

# example: two

searchuser.init("xiaolai")
searchuser.innode()
