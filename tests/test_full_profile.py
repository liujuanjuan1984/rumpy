from rumpy import FullNode

bot = FullNode()


# seed = bot.api.create_group("mytest_profiles")
bot.group_id = "47b946e4-57e1-45ed-aa78-6d591467e67e"  # seed["group_id"]

name1 = "第一次修改的昵称"
name2 = "第二次修改"

img1 = r"D:\hi.png"
img2 = r"D:\hi.jpg"
img3 = [img1, img2]

mixin_id1 = 123455
mixin_id2 = "bae95683-eabb-422f-9588-24dadffd0323"
mixin_id3 = "bae95683-eabb-422f-9588-24dadffd0300"  # FAKE
mixin_id4 = {"mixin_id": mixin_id2}
mixin_id5 = {"mixin_id": mixin_id3}


def test_profiles_update():

    resp = bot.api.update_profile(name=name1)
    print(resp)

    resp = bot.api.update_profile(name=name2)
    print(resp)

    resp = bot.api.update_profile(image=img1)
    print(resp)

    resp = bot.api.update_profile(image=img2)
    print(resp)

    try:
        resp = bot.api.update_profile(image=img3)
        print(resp)
    except:
        pass

    resp = bot.api.update_profile(mixin_id=mixin_id1)
    print(resp)

    resp = bot.api.update_profile(mixin_id=mixin_id2)
    print(resp)

    resp = bot.api.update_profile(mixin_id=mixin_id3)
    print(resp)

    try:
        resp = bot.api.update_profile(mixin_id=mixin_id4)
        print(resp)
    except:
        pass

    try:
        resp = bot.api.update_profile(mixin_id=mixin_id5)
        print(resp)
    except:
        pass

    resp = bot.api.update_profile(name=name1, image=img1, mixin_id=mixin_id2)
    print(resp)


if __name__ == "__main__":
    test_profiles_update()
