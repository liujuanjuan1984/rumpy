import datetime
from officy import Stime


def _quote(text):
    return "".join(["> ", "\n> ".join(text.split("\n")), "\n"]) if text else ""


def _nickname(pubkey, nicknames):
    try:
        name = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})"
    except:
        name = pubkey[-10:-2] or "某人"
    return name


def trx_to_newobj(client, trx, nicknames):
    """trans from trx to an object of new trx to send to chain.

    Args:
        trx (dict): the trx data
        nicknames (dict): the nicknames data of the group

    Returns:
        obj: object of NewTrx,can be used as: client.group.send_note(obj=obj).
        result: True,or False, if True, the obj can be send to chain.
    """

    if "Content" not in trx:
        return None, False

    obj = {"type": "Note", "image": []}
    ttype = trx["TypeUrl"]
    tcontent = trx["Content"]
    lines = []

    if ttype == "quorum.pb.Person":
        _name = "昵称" if "name" in tcontent else ""
        _wallet = "钱包" if "wallet" in tcontent else ""
        _image = "头像" if "image" in tcontent else ""
        _profile = "、".join([i for i in [_name, _image, _wallet] if i])
        lines.append(f"修改了个人信息：{_profile}。")
    elif ttype == "quorum.pb.Object":
        if tcontent.get("type") == "File":
            lines.append(f"上传了文件。")
        else:
            text = trx["Content"].get("content") or ""
            img = trx["Content"].get("image") or []
            lines.append(text)
            obj["image"].extend(img)

            t = client.group.trx_type(trx)
            refer_tid = None
            _info = {"like": "赞", "dislike": "踩"}
            if t == "announce":
                lines.insert(0, f"处理了链上请求。")
            elif t in _info:
                refer_tid = trx["Content"]["id"]
                refer_pubkey = client.group.trx(refer_tid).get("Publisher") or ""
                lines.insert(0, f"点{_info[t]}给 `{_nickname( refer_pubkey,nicknames)}` 所发布的内容：")
            elif t == "reply":
                lines.insert(0, f"回复说：")
                refer_tid = trx["Content"]["inreplyto"]["trxid"]
                refer_pubkey = client.group.trx(refer_tid).get("Publisher") or ""
                lines.append(f"\n回复给 `{_nickname(refer_pubkey,nicknames)}` 所发布的内容：")
            else:
                if text and img:
                    lines.insert(0, f"发布了图片，并且说：")
                elif img:
                    lines.insert(0, f"发布了图片。")
                else:
                    lines.insert(0, f"说：")

            if refer_tid:
                refer_trx = client.group.trx(refer_tid)
                refer_text = refer_trx["Content"].get("content") or ""
                refer_img = refer_trx["Content"].get("image") or []
                lines.append(_quote(refer_text))
                obj["image"].extend(refer_img)
    else:
        print(trx)
        return None, False

    obj["content"] = f'{Stime.ts2datetime(trx.get("TimeStamp"))}' + " " + "\n".join(lines)
    obj["image"] = obj["image"][:4]
    obj = {key: obj[key] for key in obj if obj[key]}

    return obj, True
