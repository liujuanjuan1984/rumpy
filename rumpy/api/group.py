import base64
import datetime
import hashlib
import json
import logging
import math
import os
import sys
import time
from typing import Any, Dict, List

from rumpy.api.base import BaseAPI
from rumpy.types.data import *
from rumpy.utils import sha256, timestamp_to_datetime

logger = logging.getLogger(__name__)

CHUNK_SIZE = 150 * 1024  # 150kb


def _quote(text):
    return "".join(["> ", "\n> ".join(text.split("\n")), "\n"]) if text else ""


def _nickname(pubkey, nicknames):
    try:
        name = nicknames[pubkey]["name"] + f"({pubkey[-10:-2]})"
    except:
        name = pubkey[-10:-2] or "某人"
    return name


def _trxs_unique(trxs: List):
    """remove the duplicate trx from the trxs list"""
    new = {}
    for trx in trxs:
        if trx["TrxId"] not in new:
            new[trx["TrxId"]] = trx
    return [new[i] for i in new]


class Group(BaseAPI):
    def create(
        self,
        group_name: str,
        app_key: str = "group_timeline",
        consensus_type: str = "poa",
        encryption_type: str = "public",
    ) -> Dict:
        """create a group, return the seed of the group.

        group_name: 组名, 自定义, 不可更改
        consensus_type: 共识类型, "poa", "pos", "pow", 当前仅支持 "poa"
        encryption_type: 加密类型, "public" 公开, "private" 私有
        app_key: 可以为自定义字段，只是如果不是 group_timeline,
            group_post, group_note 这三种，可能无法在 rum-app 中识别，
            如果是自己开发客户端，则可以自定义类型

        创建成功, 返回值是一个种子, 通过它其他人可加入该组
        """
        # check encryption_type
        if encryption_type.lower() not in ("public", "private"):
            raise ValueError("encryption_type should be `public` or `private`")

        # check consensus_type
        if consensus_type.lower() not in ("poa",):
            raise ValueError("consensus_type should be `poa` or `pos` or `pow`, but only `poa` is supported now.")

        payload = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }

        return self._post("/group", payload)

    def seed(self, group_id=None) -> Dict:
        """get the seed of a group which you've joined in."""
        group_id = group_id or self.group_id
        seed = self._get(f"/group/{group_id}/seed")
        if "error" not in seed:
            return seed
        else:
            raise ValueError(seed["error"])

    def is_seed(self, seed: Dict) -> bool:
        try:
            Seed(**seed)
            return True
        except Exception as e:
            logger.error(f"{sys._getframe().f_code.co_name}, {e}")
            return False

    def info(self):
        """return group info,type: datacalss"""
        self.check_group_joined_as_required()

        info = {}
        for _info in self._client.node.groups():
            if _info["group_id"] == self.group_id:
                info = _info
                break

        if info.get("snapshot_info") is None:
            info["snapshot_info"] = {}

        return GroupInfo(**info)

    @property
    def pubkey(self):
        return self.info().user_pubkey

    @property
    def owner(self):
        return self.info().owner_pubkey

    @property
    def eth_addr(self):
        return self.info().user_eth_addr

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        if not self.is_seed(seed):
            raise ValueError("not a seed or the seed could not be identified.")
        resp = self._post("/group/join", seed)
        if "error" in resp:
            if resp["error"] == "Group with same GroupId existed":
                resp = True
            else:
                raise ValueError(resp["error"])
        return resp

    def is_joined(self, group_id=None) -> bool:
        group_id = group_id or self.group_id
        if group_id in self._client.node.groups_id:
            return True
        return False

    def leave(self, group_id=None):
        """leave a group"""
        group_id = group_id or self.group_id
        return self._post("/group/leave", {"group_id": group_id})

    def clear(self, group_id=None):
        """clear data of a group"""
        group_id = group_id or self.group_id
        return self._post("/group/clear", {"group_id": group_id})

    def startsync(self, group_id=None):
        """触发同步"""
        group_id = group_id or self.group_id
        return self._post(f"/group/{group_id}/startsync")

    def content_trxs(
        self,
        is_reverse: bool = False,
        trx_id: str = None,
        num: int = 20,
        is_include_starttrx: bool = False,
        senders: List = None,
    ) -> List:
        """requests the content trxs of a group,return the list of the trxs data.

        按条件获取某个组的内容并去重返回

        is_reverse: 默认按顺序获取, 如果是 True, 从最新的内容开始获取
        trx_id: 某条内容的 Trx ID, 如果提供, 从该条之后(不包含)获取
        num: 要获取内容条数, 默认获取最前面的 20 条内容
        is_include_starttrx: 如果是 True, 获取内容包含 Trx ID 这条内容
        """
        if not self.is_joined():
            return []

        if trx_id:
            apiurl = f"/group/{self.group_id}/content?num={num}&starttrx={trx_id}&reverse={str(is_reverse).lower()}&includestarttrx={str(is_include_starttrx).lower()}"
        else:
            apiurl = f"/group/{self.group_id}/content?num={num}&reverse={str(is_reverse).lower()}"

        trxs = self._post(apiurl, api_base=self._client.api_base_app) or []
        return _trxs_unique(trxs)

    def _send(self, obj=None, sendtype=None, **kwargs) -> Dict:
        """return the {trx_id:trx_id} of this action if send successded

        obj: 要发送的对象
        sendtype: 发送类型, "Add"(发送内容), "Like"(点赞), "Dislike"(点踩)
        返回值 {"trx_id": "string"}
        """
        payload = NewTrx(group_id=self.group_id, obj=obj, sendtype=sendtype, **kwargs).__dict__
        return self._post("/group/content", payload)

    def like(self, trx_id: str) -> Dict:
        return self._send(trx_id=trx_id, sendtype="Like")

    def dislike(self, trx_id: str) -> Dict:
        return self._send(trx_id=trx_id, sendtype="Dislike")

    def _file_to_objs(self, file_path):
        import filetype

        file_total_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path).encode().decode("utf-8")
        file_obj = open(file_path, "rb")
        fileinfo = {
            "mediaType": filetype.guess(file_path).mime,
            "name": file_name,
            "title": file_name.split(".")[0],
            "sha256": sha256(file_obj.read()),
            "segments": [],
        }

        chunks = math.ceil(file_total_size / CHUNK_SIZE)
        objs = []

        for i in range(chunks):
            if i + 1 == chunks:
                current_size = file_total_size % CHUNK_SIZE
            else:
                current_size = CHUNK_SIZE
            file_obj.seek(i * CHUNK_SIZE)
            ibytes = file_obj.read(current_size)
            fileinfo["segments"].append({"id": f"seg-{i+1}", "sha256": sha256(ibytes)})
            obj = FileObj(
                name=f"seg-{i + 1}",
                content=ibytes,
                mediaType="application/octet-stream",
            )
            objs.append(obj)

        content = json.dumps(fileinfo).encode()
        obj = FileObj(content=content, name="fileinfo", mediaType="application/json")

        objs.insert(0, obj)
        file_obj.close()
        return objs

    def upload(self, file_path):
        if not os.path.isfile(file_path):
            logger.info(f"{sys._getframe().f_code.co_name}, {file_path} is not a file.")
            return
        for obj in self._file_to_objs(file_path):
            self._send(obj=obj, sendtype="Add")

    def _file_infos(self, trx_id=None):
        trxs = self.all_content_trxs(trx_id)
        infos = []
        filetrxs = []
        for trx in trxs:
            if trx["Content"].get("name") == "fileinfo":
                info = eval(base64.b64decode(trx["Content"]["file"]["content"]).decode("utf-8"))
                logger.debug(f"{sys._getframe().f_code.co_name}, {info}")
                infos.append(info)
            if trx["Content"].get("type") == "File":
                filetrxs.append(trx)
        return infos, filetrxs

    def _down_load(self, file_dir, info, trxs):

        ifilepath = os.path.join(file_dir, info["name"])
        if os.path.exists(ifilepath):
            logger.info(f"{sys._getframe().f_code.co_name}, file exists {ifilepath}")
            return

        # _check_trxs
        right_shas = [i["sha256"] for i in info["segments"]]
        contents = {}

        for trx in trxs:
            content = base64.b64decode(trx["Content"]["file"]["content"])
            csha = hashlib.sha256(content).hexdigest()
            if csha in right_shas:
                contents[csha] = trx

        flag = True

        for seg in info["segments"]:
            if seg["sha256"] not in contents:
                logger.info(f"{sys._getframe().f_code.co_name}, " + json.dumps(seg) + ", trx is not exists...")
                flag = False
                break
            if contents[seg["sha256"]]["Content"].get("name") != seg["id"]:
                logger.info(f"{sys._getframe().f_code.co_name}, " + json.dumps(seg) + ", name is different...")
                flag = False
                break

        if flag:
            ifile = open(ifilepath, "wb+")
            for seg in info["segments"]:
                content = base64.b64decode(contents[seg["sha256"]]["Content"]["file"]["content"])
                ifile.write(content)
            ifile.close()
            logger.info(f"{sys._getframe().f_code.co_name}, {ifilepath}, downloaded!")

    def download(self, file_dir):
        logger.debug(f"download file to dir {file_dir} start...")
        infos, trxs = self._file_infos()
        for info in infos:
            self._down_load(file_dir, info, trxs)
        logger.debug(f"download file to dir {file_dir} done")

    def send_note(self, **kwargs):
        return self._send(sendtype="Add", objtype="Note", **kwargs)

    def reply(self, content: str, trx_id: str, images=None):
        """回复某条内容(仅图片, 仅文本, 或两者都有)

        trx_id: 要回复的内容的 Trx ID
        content: 用于回复的文本内容
        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
            content 和 images 必须至少一个不是 None
        """
        return self.send_note(content=content, images=images, inreplyto=trx_id)

    def send_text(self, content: str, name: str = None):
        """post text cotnent to group

        content: 要发送的文本内容
        name: 内容标题, 例如 rum-app 论坛模板必须提供的文章标题
        """
        return self.send_note(content=content, name=name)

    def send_img(self, images):
        """post images to group

        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
        """
        if type(images) != list:
            images = [images]
        return self.send_note(images=images)

    def block(self, block_id: str):
        """get the info of a block in a group"""
        self.check_group_id_as_required()
        return self._get(f"/block/{self.group_id}/{block_id}")

    def is_owner(self) -> bool:
        """return True if I create this group else False"""
        ginfo = self.info()
        if isinstance(ginfo, GroupInfo) and ginfo.owner_pubkey == ginfo.user_pubkey:
            return True
        return False

    def all_content_trxs(self, trx_id: str = None, senders=None):
        """get all the trxs of content started from trx_id"""
        trxs = []
        checked_trxids = []
        senders = senders or []
        while True:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            newtrxs = self.content_trxs(trx_id=trx_id, num=100)
            if len(newtrxs) == 0:
                break
            if senders:
                trxs.extend([itrx for itrx in newtrxs if itrx.get("Publisher") in senders])
            else:
                trxs.extend(newtrxs)
            trx_id = self.last_trx_id(trx_id, newtrxs)
        return trxs

    def last_trx_id(self, trx_id: str, trxs: List):
        """get the last-trx_id of trxs which if different from given trx_id"""
        for i in range(-1, -1 * len(trxs), -1):
            tid = trxs[i]["TrxId"]
            if tid != trx_id:
                return tid
        return trx_id

    def trx_type(self, trxdata: Dict):
        """get type of trx, trx is one of group content list"""
        if "TypeUrl" not in trxdata:
            return "encrypted"
        if trxdata["TypeUrl"] == "quorum.pb.Person":
            return "person"
        content = trxdata["Content"]
        trxtype = content.get("type", "other")
        if type(trxtype) == int:
            return "announce"
        if trxtype == "Note":
            if "inreplyto" in content:
                return "reply"
            if "image" in content:
                if "content" not in content:
                    return "image_only"
                else:
                    return "image_text"
            return "text_only"
        return trxtype.lower()  # "like","dislike","other"

    def trx(self, trx_id: str):
        """get trx data by trx_id"""
        self.check_group_id_as_required()
        data = {}
        trxs = self.content_trxs(trx_id=trx_id, num=1, is_include_starttrx=True)
        if len(trxs) > 1:
            raise ValueError(f"{len(trxs)} trxs got from group: <{self.group_id}> with trx: <{trx_id}>.")
        elif len(trxs) == 1:
            data = trxs[0]
        else:
            data = self._get(f"/trx/{self.group_id}/{trx_id}")
            logger.info(f"data is encrypted for trx: <{trx_id}> of group: <{self.group_id}>.")
        if not data:
            logger.warning(f"data is empty for trx: <{trx_id}> of group: <{self.group_id}>.")
        return data

    def pubqueue(self):
        self.check_group_id_as_required()
        resp = self._get(f"/group/{self.group_id}/pubqueue")
        return resp.get("Data")

    def ack(self, trx_ids: List):
        return self._post("/trx/ack", {"trx_ids": trx_ids})

    def autoack(self):
        self.check_group_id_as_required()
        tids = [i["Trx"]["TrxId"] for i in self.pubqueue() if i["State"] == "FAIL"]
        return self.ack(tids)

    def get_users_profiles(self, users_data: Dict = {}, types=("name", "image", "wallet")) -> Dict:
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
        group_id = users_data.get("group_id", self.group_id)
        if group_id != self.group_id:
            logger.warning(
                f"get_users_profiles: group_id is different. client.group_id:{self.group_id}, data.group_id:{group_id}"
            )
            return users_data

        # get new trxs from the trx_id
        trx_id = users_data.get("trx_id", None)
        trxs = self.all_content_trxs(trx_id=trx_id)

        if len(trxs) == 0:
            logger.debug(f"get_users_profiles: got 0 new trxs. get content started from trx_id:{trx_id}.")
            return users_data

        # update trx_id: to record the progress to get new trxs

        users_data.update(
            {
                "group_id": self.group_id,
                "group_name": self.seed().get("group_name"),
                "trx_id": trxs[-1]["TrxId"],
                "trx_timestamp": str(timestamp_to_datetime(trxs[-1].get("TimeStamp", ""))),
            }
        )

        users = users_data.get("data", {})
        profile_trxs = [trx for trx in trxs if trx.get("TypeUrl") == "quorum.pb.Person"]

        for trx in profile_trxs:
            if "Content" not in trx:
                continue
            pubkey = trx["Publisher"]
            if pubkey not in users:
                users[pubkey] = {}
            for key in trx["Content"]:
                if key in types:
                    users[pubkey].update({key: trx["Content"][key]})
        users_data.update({"data": users, "update_at": str(datetime.datetime.now())})
        return users_data

    def trx_to_newobj(self, trx, nicknames, refer_trx=None):
        """trans from trx to an object of new trx to send to chain.

        Args:
            trx (dict): the trx data
            nicknames (dict): the nicknames data of the group

        Returns:
            obj: object of NewTrx,can be used as: self.send_note(obj=obj).
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
                text = trx["Content"].get("content", "")
                img = trx["Content"].get("image", [])
                lines.append(text)
                obj["image"].extend(img)

                t = self.trx_type(trx)
                refer_tid = None
                _info = {"like": "赞", "dislike": "踩"}
                if t == "announce":
                    lines.insert(0, f"处理了链上请求。")
                elif t in _info:
                    refer_tid = trx["Content"]["id"]
                    refer_pubkey = self.trx(refer_tid).get("Publisher", "")
                    lines.insert(
                        0,
                        f"点{_info[t]}给 `{_nickname( refer_pubkey,nicknames)}` 所发布的内容：",
                    )
                elif t == "reply":
                    lines.insert(0, f"回复说：")
                    refer_tid = trx["Content"]["inreplyto"]["trxid"]
                    refer_pubkey = self.trx(refer_tid).get("Publisher", "")
                    lines.append(f"\n回复给 `{_nickname(refer_pubkey,nicknames)}` 所发布的内容：")
                else:
                    if text and img:
                        lines.insert(0, f"发布了图片，并且说：")
                    elif img:
                        lines.insert(0, f"发布了图片。")
                    else:
                        lines.insert(0, f"说：")

                if refer_tid:

                    refer_trx = refer_trx or self.trx(refer_tid)
                    if "Content" in refer_trx:
                        refer_text = refer_trx["Content"].get("content", "")
                        refer_img = refer_trx["Content"].get("image", [])
                        lines.append(_quote(refer_text))
                        obj["image"].extend(refer_img)
        else:
            return None, False

        obj["content"] = f'{timestamp_to_datetime(trx.get("TimeStamp"))}' + " " + "\n".join(lines)
        obj["image"] = obj["image"][:4]
        obj = {key: obj[key] for key in obj if obj[key]}

        return obj, True
