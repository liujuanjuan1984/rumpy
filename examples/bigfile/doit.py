from filebot import FileBot
from officy import Dir

bot = FileBot(port=55883)
bot.group_id = "8da0023a-9dba-409f-b18b-f2edd3a73251"

asku = input("0 byebye\n1 upload\n2 download\n>>")

if asku == "1":
    # upload files
    file_path = r"D:\books\73198_171789_他者的消失.epub"
    bot.upload(file_path)

    file_path = r"D:\002e7WLugy1gu9dy8xdwxj612v0u07bh02.jpg"
    bot.upload(file_path)

    file_path = r"D:\telegram download\441444b9ab3896f3ebcd78297920693a.mp4"
    bot.upload(file_path)

elif asku == "2":
    # download files
    file_dir = r"D:\test_download"
    Dir(file_dir).check()
    bot.download(file_dir)

else:
    print("byebye.")
