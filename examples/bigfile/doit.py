import os

from officy import JsonFile

from rumpy import FullNode

bot = FullNode(port=62663)


def check_group():
    seedfile = os.path.join(os.path.dirname(__file__), "group_seed.json")

    seed = JsonFile(seedfile).read({}) or bot.api.create_group("mytest_bigfile")
    JsonFile(seedfile).write(seed)

    bot.group_id = seed["group_id"]

    if not bot.api.is_joined():
        JsonFile(seedfile).write({})
        check_group()


asku = input("0 byebye\n1 upload\n2 download\n>>")
check_group()
if asku == "1":
    # upload files
    file_path = r"D:\books\73198_171789_他者的消失.epub"
    bot.api.upload_file(file_path)

    file_path = r"D:\002e7WLugy1gu9dy8xdwxj612v0u07bh02.jpg"
    bot.api.upload_file(file_path)

    file_path = r"D:\telegram download\441444b9ab3896f3ebcd78297920693a.mp4"
    bot.api.upload_file(file_path)

elif asku == "2":
    # download files
    file_dir = r"D:\test_download"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    bot.api.download_file(file_dir)

else:
    print("byebye.")
