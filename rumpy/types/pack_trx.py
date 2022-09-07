from typing import Dict, List

from rumpy.types.data import *


def pack_person_trx(group_id: str, name: str = None, image=None, wallet=None) -> Dict:
    obj = PersonObj(name, image, wallet).to_dict()
    trx = NewTrxBase("Update", group_id, person=obj).to_dict()
    return trx


def pack_note_trx(
    group_id: str,
    content: str = None,
    name: str = None,
    images: List = None,
    edit_trx_id: str = None,
    del_trx_id: str = None,
    reply_trx_id: str = None,
) -> Dict:
    obj = ContentObj(content, name, images, edit_trx_id, del_trx_id, reply_trx_id).to_dict()
    trx = NewTrxBase("Add", group_id, object=obj).to_dict()
    return trx


def pack_like_trx(group_id, trx_id, like_type="Like"):
    obj = {"id": trx_id}
    if like_type.lower() not in ("like", "dislike"):
        err = f"param type should be Like or Dislike"
        raise ParamOverflowError(err)
    like_type = like_type.title()
    trx = NewTrxBase(like_type, group_id, object=obj).to_dict()
    return trx
