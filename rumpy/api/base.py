import base64
import logging
import os
from typing import Any, Dict, List

import rumpy.utils as utils
from rumpy.client._requests import HttpRequest

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
            raise ValueError("group_id is required, now it's None.")
        return group_id

    def check_group_joined_as_required(self, group_id=None):
        group_id = self.check_group_id_as_required(group_id)
        if group_id not in self._http.api.groups_id:
            raise ValueError(f"You are not in this group: <{group_id}>.")
        return group_id

    def check_group_owner_as_required(self, group_id=None):
        group_id = self.check_group_joined_as_required(group_id)
        info = self._http.api.group_info(group_id)
        if info.user_pubkey != info.owner_pubkey:
            raise ValueError(f"You are not the owner of this group: <{group_id}>.")
        return group_id

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

    def raise_error(self, resp, except_err=None):
        if err := resp.get("error"):
            if err != except_err:
                raise ValueError(err)
        return resp

    def like(self, trx_id: str, group_id=None) -> Dict:
        return self._http.api._send(like_trx_id=trx_id, activity_type="Like", group_id=group_id)

    def dislike(self, trx_id: str, group_id=None) -> Dict:
        return self._http.api._send(like_trx_id=trx_id, activity_type="Dislike", group_id=group_id)

    def __send_note(self, group_id=None, **kwargs):
        return self._http.api._send(group_id=group_id, activity_type="Add", object_type="Note", **kwargs)

    def send_note(self, content: str = None, images: List = None, name=None, group_id=None):
        return self.__send_note(content=content, images=images, name=None, group_id=group_id)

    def del_note(self, trx_id, group_id=None):
        return self.__send_note(del_trx_id=trx_id, group_id=group_id)

    def edit_note(self, trx_id, content: str = None, images: List = None, group_id=None):
        return self.__send_note(
            edit_trx_id=trx_id,
            content=content,
            images=images,
            group_id=group_id,
        )

    def reply(self, trx_id: str, content: str = None, images=None, group_id=None):
        return self.__send_note(
            reply_trx_id=trx_id,
            content=content,
            images=images,
            group_id=group_id,
        )

    def trx_to_newobj(self, trx, group_id=None):
        """trans from trx to an object of new trx to send to chain.
        Returns:
            obj: object of NewTrx,can be used as: self.send_note(obj=obj).
        """

        refer_trx = self._http.api.trx(utils.get_refer_trxid(trx), group_id)
        params = utils.rx_retweet_params_init(trx, refer_trx)
        return params

    def search_file_trxs(self, trx_id=None, group_id=None):
        trxs = self._http.api.all_content_trxs(trx_id, group_id=group_id)
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

    def upload_file(self, file_path, group_id=None):
        if not os.path.isfile(file_path):
            logger.warning(f"{file_path} is not a file.")
            return
        for obj in utils.split_file_to_trx_objs(file_path):
            resp = self._http.api._send(obj=obj, activity_type="Add", group_id=group_id)

    def download_files(self, file_dir, group_id=None):
        infos, trxs = self.search_file_trxs(group_id)
        utils.merge_trxs_to_files(file_dir, infos, trxs)
