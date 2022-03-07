import os
from rumpyconfig import RumpyConfig
from officepy import JsonFile
from search_user import SearchUser

searchuser = SearchUser(**RumpyConfig.GUI)
seedsfile = RumpyConfig.SEEDSFILE
# example: one

searchuser.init("huoju", seedsfile)
searchuser.innode()

# example: two

searchuser.init("xiaolai", seedsfile)
searchuser.innode()
