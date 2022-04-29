import os
from officy import Dir, JsonFile
import sys

sys.path.insert(0, r"D:\Jupyter\rumpy")
from rumpy import RumClient

bot = RumClient(port=58356)

seedfile = os.path.join(os.path.dirname(__file__), "group_seed.json")

if os.path.exists(seedfile):
    seed = JsonFile(seedfile).read()
else:
    seed = bot.group.create("mytest_bigfile")
    JsonFile(seedfile).write(seed)

bot.group_id = seed["group_id"]


asku = input("0 byebye\n1 upload\n2 download\n>>")

if asku == "1":
    # upload files
    file_path = r"D:\books\73198_171789_他者的消失.epub"
    bot.group.upload(file_path)

    file_path = r"D:\002e7WLugy1gu9dy8xdwxj612v0u07bh02.jpg"
    bot.group.upload(file_path)

    file_path = r"D:\telegram download\441444b9ab3896f3ebcd78297920693a.mp4"
    bot.group.upload(file_path)

elif asku == "2":
    # download files
    file_dir = r"D:\test_download"
    Dir(file_dir).check()
    bot.group.download(file_dir)

else:
    print("byebye.")
