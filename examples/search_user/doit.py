import os

from officy import JsonFile
from search_user import SearchUser

searchuser = SearchUser()
seedsfile = r"D:\Jupyter\seeds\data\seeds.json"
# example: one

searchuser.init("huoju", seedsfile)
searchuser.innode()

# example: two

searchuser.init("xiaolai", seedsfile)
searchuser.innode()
