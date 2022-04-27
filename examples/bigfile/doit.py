from filebot import FileBot


bot = FileBot(port=55883)
bot.init(group_name="mytest_epub_他者的消失")
file_path = r"D:\books\73198_171789_他者的消失.epub"
bot.upload(file_path)
