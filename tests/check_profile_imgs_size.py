import base64

import rumpy.utils as utils
from rumpy import FullNode

bot = FullNode()

group_id = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"


def check_profile_image_size():
    # 检查 profiles 的 image 的字节大小，是否超出了 200 kb
    trxs = bot.api.get_group_all_contents(trx_types=("person",), group_id=group_id)
    rlts = []
    for trx in trxs:
        img = trx["Content"].get("image", {}).get("content", "")
        imgb = base64.b64decode(img)
        size = len(imgb) // 1024
        if size > 200:
            print(size, "kb", utils.trx_timestr(trx, "str"))
            rlts.append(size)
    print(rlts)
    # [224, 359, 316, 208, 208, 255, 320, 411, 411]


def check_profile_image_dumplicate():
    # 检查 profiles 的 image 的重复度，用 hash 来计算。
    trxs = bot.api.get_group_all_contents(trx_types=("person",), group_id=group_id)
    rlts = {}
    for trx in trxs:
        img = trx["Content"].get("image", {}).get("content", "")
        imgb = base64.b64decode(img)
        imgsha = utils.sha256(imgb)
        rlts[imgsha] = rlts.get(imgsha, 0) + 1

    for k, v in rlts.items():
        if v > 1:
            print(k, v)


def check_trx_image_sizes():
    # 检查用户上传的图片，是否超出 200 kb

    trxs = bot.api.get_group_all_contents(trx_types=("image_only", "image_text"), group_id=group_id)
    rlts = []
    all_rlts = []
    for trx in trxs:
        imgs = trx["Content"].get("image", [])
        _sizes = 0
        for img in imgs:
            imgb = base64.b64decode(img.get("content", ""))
            size = len(imgb) // 1024
            print(size, "kb", "TOO BIG!" if size > 200 else "")
            if size > 200:
                rlts.append(size)
            _sizes += size
        if _sizes > 200:
            all_rlts.append(_sizes)

    print("单张图片超出 200kb: ", rlts)  # []
    print("单条 trxs 的图片总大小超出 200kb: ", all_rlts)  # []


if __name__ == "__main__":
    check_profile_image_dumplicate()
