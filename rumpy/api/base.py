import base64
import datetime
import json
import logging
import os
from typing import Any, Dict, List

import rumpy.utils as utils
from rumpy.client._requests import HttpRequest
from rumpy.exceptions import *
from rumpy.types.data import *
from rumpy.types.pack_trx import *

logger = logging.getLogger(__name__)


class BaseAPI:
    def __init__(self, http: HttpRequest = None):
        self._http = http

    def _get(self, endpoint: str, payload: Dict = {}):
        api_base = None
        if hasattr(self, "API_BASE"):
            api_base = self.API_BASE
        return self._http.get(endpoint, payload, api_base)

    def _post(self, endpoint: str, payload: Dict = {}):
        api_base = None
        if hasattr(self, "API_BASE"):
            api_base = self.API_BASE
        return self._http.post(endpoint, payload, api_base)

    def check_group_id_as_required(self, group_id=None):
        group_id = group_id or self._http.group_id
        if not group_id:
            raise ParamValueError("group_id is required, now it's None.")
        return group_id

    def check_group_joined_as_required(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        if group_id not in self._http.api.groups_id:
            raise RumChainException(f"You are not in this group: <{group_id}>.")
        return group_id

    def check_group_owner_as_required(self, group_id=None):
        group_id = self.check_group_joined_as_required(group_id)
        info = self._http.api.group_info(group_id)
        if info.get("user_pubkey", "user") != info.get("owner_pubkey", "owner"):
            raise RumChainException(f"You are not the owner of this group: <{group_id}>.")
        return group_id

    def groups(self) -> List:
        resp = self._http.api._groups()
        if "groups" in resp:
            return resp["groups"] or []
        raise RumException(json.dumps(resp))

    @property
    def groups_id(self) -> List:
        """return list of group_id which node has joined"""
        return [i["group_id"] for i in self.groups()]

    @property
    def group_name(self):
        self.check_group_joined_as_required(group_id)
        url = self.api.seed()["seed"]
        return utils.group_name(url)

    def is_joined(self, group_id=None) -> bool:
        try:
            self.check_group_joined_as_required(group_id)
            return True
        except:
            return False

    def is_owner(self, group_id=None) -> bool:
        """return True if I create this group else False"""
        try:
            self.check_group_owner_as_required(group_id)
            return True
        except:
            return False

    def raise_error(self, resp, except_err=None):  # TODO:这个封装，语义上不好，暂时没有调用。
        if err := resp.get("error"):
            if err != except_err:
                raise RumChainException(err)
        return resp

    def like(self, trx_id: str, group_id=None, like_type="Like") -> Dict:
        group_id = self.check_group_joined_as_required(group_id)
        trx = pack_like_trx(group_id, trx_id, like_type)
        return self._http.api._post_trx(trx)

    def dislike(self, trx_id: str, group_id=None) -> Dict:
        return self.like(trx_id, group_id, "Dislike")

    def __post_content(self, group_id=None, **kwargs):
        group_id = self.check_group_joined_as_required(group_id)
        trx = pack_note_trx(group_id, **kwargs)
        return self._http.api._post_trx(trx)

    def send_note(self, content: str = None, images: List = None, name=None, group_id=None):
        return self.__post_content(content=content, images=images, name=name, group_id=group_id)

    def del_note(self, trx_id, group_id=None):
        return self.__post_content(del_trx_id=trx_id, group_id=group_id)

    def edit_note(
        self,
        trx_id,
        content: str = None,
        images: List = None,
        name=None,
        group_id=None,
    ):
        return self.__post_content(
            edit_trx_id=trx_id,
            content=content,
            images=images,
            name=name,
            group_id=group_id,
        )

    def reply(self, trx_id: str, content: str = None, images=None, group_id=None):
        return self.__post_content(
            reply_trx_id=trx_id,
            content=content,
            images=images,
            group_id=group_id,
        )

    def update_profile(
        self,
        name=None,
        image=None,
        wallet: Union[str, Dict, None] = None,
        group_id=None,
    ):
        """user update the profile: name, image, or wallet.

        name: nickname of user
        image: one image, as file_path or bytes or bytes-string
        wallet:
        """
        group_id = self.check_group_joined_as_required(group_id)
        trx = pack_person_trx(group_id, name, image, wallet)
        return self._http.api._update_profile(trx)

    def trx(self, trx_id: str, group_id=None):
        """get trx data by trx_id"""
        data = {}
        if not trx_id:
            return data

        trxs = self._http.api.get_group_content(
            trx_id=trx_id, num=1, includestarttrx=True, group_id=group_id
        )
        if len(trxs) > 1:
            raise ParamOverflowError(
                f"{len(trxs)} trxs got from group: <{group_id}> with trx: <{trx_id}>.",
            )
        elif len(trxs) == 1:
            data = trxs[0]
        else:
            data = self._http.api.get_trx(trx_id=trx_id, group_id=group_id)
        return data

    def upload_file(self, file_path, group_id=None, is_zip=False):
        utils.check_file(file_path)
        group_id = self.check_group_joined_as_required(group_id)

        if is_zip:
            file_path = utils.zip_file(file_path)
            utils.check_file(file_path)

        for piece in utils.split_file_to_pieces(file_path):
            trx = NewTrxFile(group_id, **piece).to_dict()
            resp = self._http.api._post_trx(trx)

    def download_files(self, file_dir, group_id=None):
        utils.check_dir(file_dir)
        infos, trxs = self.search_file_trxs(group_id=group_id)
        utils.merge_trxs_to_files(file_dir, infos, trxs)

    def get_contents(
        self,
        trx_id=None,
        group_id=None,
        senders=None,
        trx_types=None,
        reverse=False,
        num=20,
    ):
        """返回的是一个生成器，可以用 for ... in ... 来迭代访问。trx_types 的取值见 utils.trx_type() 的各种返回值"""
        trxs = self._http.api.get_group_content(
            group_id=group_id, trx_id=trx_id, num=num, reverse=reverse
        )
        checked_trxids = []
        trx_types = trx_types or []
        senders = senders or []
        got_num = 0
        stop = False
        while trxs and not stop:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            for trx in trxs:
                if got_num < num:
                    flag1 = (utils.trx_type(trx) in trx_types) or (not trx_types)
                    flag2 = (trx.get("Publisher", "") in senders) or (not senders)
                    if flag1 and flag2:
                        got_num += 1
                        yield trx
                else:
                    stop = True
                    break
            if stop:
                break
            trx_id = utils.get_last_trxid_by_chain(trx_id, trxs, reverse=reverse)
            trxs = self._http.api.get_group_content(
                group_id=group_id, trx_id=trx_id, num=num, reverse=reverse
            )

    def get_group_all_contents(
        self,
        trx_id=None,
        group_id=None,
        senders=None,
        trx_types=None,
        reverse=False,
    ):
        """返回的是一个生成器，可以用 for ... in ... 来迭代访问。trx_types 的取值见 utils.trx_type() 的各种返回值"""
        trxs = self._http.api.get_group_content(
            group_id=group_id, trx_id=trx_id, num=200, reverse=reverse
        )
        checked_trxids = []
        trx_types = trx_types or []
        senders = senders or []
        while trxs:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            for trx in trxs:
                flag1 = (utils.trx_type(trx) in trx_types) or (not trx_types)
                flag2 = (trx.get("Publisher", "") in senders) or (not senders)
                if flag1 and flag2:
                    yield trx
            trx_id = utils.get_last_trxid_by_chain(trx_id, trxs, reverse=reverse)
            trxs = self._http.api.get_group_content(
                group_id=group_id, trx_id=trx_id, num=200, reverse=reverse
            )

    def get_profiles(
        self,
        trx_id=None,
        types=("name", "image", "wallet"),
        group_id=None,
        pubkey=None,
        users=None,  # 已有的data，传入可用来更新数据
    ):
        group_id = self.check_group_id_as_required(group_id)
        senders = [pubkey] if pubkey else None
        trxs = self.get_group_all_contents(
            trx_id=trx_id,
            group_id=group_id,
            trx_types=["person"],
            senders=senders,
            reverse=False,
        )
        users = users or {}
        progress_tid = trx_id
        for trx in trxs:
            progress_tid = trx["TrxId"]
            if trx_content := trx.get("Content"):
                pubkey = trx["Publisher"]
                if pubkey not in users:
                    users[pubkey] = {}
                for key in trx_content:
                    if key in types:
                        users[pubkey].update({key: trx_content[key]})
        users["progress_tid"] = progress_tid
        return users

    def update_profiles_data(
        self,
        users_data: Dict = {},
        types=("name", "image", "wallet"),
        group_id=None,
        pubkey=None,
    ) -> Dict:
        """update users_data and returns it.
        {
            group_id:  "", # the group_id
            group_name: "", # the group_name
            trx_id: "", # the trx_id of groups progress
            trx_timestamp:"",
            update_at: "",
            data:{ pubkey:{
                name:"",
                image:{},
                wallet:[],
                }
            }
        }
        """
        # check group_id

        group_id = users_data.get("group_id") or self.check_group_id_as_required(group_id)
        group_id = self.check_group_joined_as_required(group_id)

        # get new trxs from the trx_id
        trx_id = users_data.get("trx_id", None)
        users = users_data.get("data", {})
        users = self.get_profiles(
            users=users,
            trx_id=trx_id,
            types=types,
            group_id=group_id,
            pubkey=pubkey,
        )
        progress_tid = users["progress_tid"]
        try:
            _ts = self._http.api.trx(group_id=group_id, trx_id=progress_tid)["TimeStamp"]
            _dt = utils.timestamp_to_datetime(_ts)
        except TypeError:
            _dt = None

        _now = datetime.datetime.now()
        users_data.update(
            {
                "group_id": group_id,
                "trx_id": progress_tid,
                "trx_timestamp": str(_dt or _now),
                "data": users,
                "update_at": str(_now),
            }
        )
        return users_data

    def trx_retweet_params(self, trx, group_id=None, nicknames=None):
        """trans from trx to an object of new trx to send to chain.
        Returns:
            obj: object of new trx,can be used as: self.send_note(obj=obj).
        """

        refer_tid = utils.get_refer_trxid(trx)
        refer_trx = None
        if refer_tid:
            refer_trx = self._http.api.trx(trx_id=refer_tid, group_id=group_id)
        params = utils.trx_retweet_params_init(trx=trx, refer_trx=refer_trx, nicknames=nicknames)
        return params

    def search_file_trxs(self, trx_id=None, group_id=None):
        trxs = self.get_group_all_contents(trx_id=trx_id, group_id=group_id)
        infos = []
        filetrxs = []
        for trx in trxs:
            if trx["Content"].get("name") == "fileinfo":
                info = eval(base64.b64decode(trx["Content"]["file"]["content"]).decode("utf-8"))
                logger.debug(f"{info}")
                infos.append(info)
            if trx["Content"].get("type") == "File":
                filetrxs.append(trx)
        return infos, filetrxs
