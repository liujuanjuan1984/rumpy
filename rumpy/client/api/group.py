from typing import List, Dict, Any
from rumpy.client.api.base import BaseAPI
from rumpy.client.api.data import *
from rumpy.client.api.img import Img


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

        if encryption_type.lower() not in ["public", "private"]:
            raise ValueError("encryption_type should be `public` or `private`")

        relay = {
            "group_name": group_name,
            "consensus_type": consensus_type,
            "encryption_type": encryption_type,
            "app_key": app_key,
        }

        return self._post(f"{self.baseurl}/group", relay)

    def seed(self) -> Dict:
        """get the seed of a group which you've joined in."""
        if self.is_joined():
            seed = self._get(f"{self.baseurl}/group/{self.group_id}/seed")
            if "error" not in seed:
                return seed

    def is_seed(self, seed: Dict) -> bool:
        try:
            Seed(**seed)
            return True
        except Exception as e:
            print(e)
            return False

    def info(self):
        """return group info,type: datacalss"""
        if self.is_joined():
            for info in self.node.groups():
                if info["group_id"] == self.group_id:
                    return GroupInfo(**info)
        else:
            raise ValueError(f"you are not in this group.{self.group_id}")

    @property
    def pubkey(self):
        return self.info().user_pubkey

    @property
    def owner(self):
        return self.info().owner_pubkey

    @property
    def eth_addr(self):
        return self.info().user_eth_addr

    @property
    def type(self):
        self._check_group_id()
        return self.seed().get("app_key")

    def join(self, seed: Dict):
        """join a group with the seed of the group"""
        if not self.is_seed(seed):
            raise ValueError("not a seed or the seed could not be identified.")
        return self._post(f"{self.baseurl}/group/join", seed)

    def is_joined(self) -> bool:
        self._check_group_id()
        if self.group_id in self.node.groups_id:
            return True
        return False

    def leave(self):
        """leave a group"""
        if self.is_joined():
            return self._post(f"{self.baseurl}/group/leave", {"group_id": self.group_id})

    def clear(self):
        """clear data of a group"""
        self._check_group_id()
        return self._post(f"{self.baseurl}/group/clear", {"group_id": self.group_id})

    def startsync(self):
        """触发同步"""
        if self.is_joined():
            return self._post(f"{self.baseurl}/group/{self.group_id}/startsync")

    def content(self) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        if self.is_joined():
            return self._get(f"{self.baseurl}/group/{self.group_id}/content") or []

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
            apiurl = (
                f"{self.baseurl_app}/group/{self.group_id}/content?num={num}&starttrx={trx_id}"
                f"&reverse={str(is_reverse).lower()}&includestarttrx={str(is_include_starttrx).lower()}"
            )
        else:
            apiurl = f"{self.baseurl_app}/group/{self.group_id}/content?num={num}&reverse={str(is_reverse).lower()}"

        trxs = self._post(apiurl) or []
        return self.trxs_unique(trxs)

    def _send(self, obj: Dict, sendtype: str = "Add") -> Dict:
        """return the {trx_id:trx_id} of this action if send successded

        obj: 要发送的对象
        sendtype: 发送类型, "Add"(发送内容), "Like"(点赞), "Dislike"(点踩)
        返回值 {"trx_id": "string"}
        """

        self._check_group_id()
        if sendtype not in [4, "Add", "Like", "Dislike"]:
            sendtype = "Add"

        relay = {
            "type": sendtype,
            "object": obj,
            "target": {"id": self.group_id, "type": "Group"},
        }

        return self._post(f"{self.baseurl}/group/content", relay)

    def like(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Like")

    def dislike(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Dislike")

    def send_note(
        self,
        content: str = None,
        name: str = None,
        images: List = None,
        update_id: str = None,
        inreplyto: str = None,
    ):
        """send note to a group. can be used to send: text only, image only,
        text with image, reply...etc

        content: str,text
        name:str, title for group_post if needed
        images: list of images, such as imgpath, or imgbytes, or rum-trx-img-objs

        发送/回复内容到一个组(仅图片, 仅文本, 或两者都有)

        content: 要发送的文本内容
        name: 内容标题, 例如 rum-app 论坛模板必须提供的文章标题
        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
            content 和 images 必须至少一个不是 None
        update_id: 自己已经发送成功的某条 Trx 的 ID, rum-app 用来标记, 如果提供该参数,
            再次发送一条消息, 前端将只显示新发送的这条, 从而实现更新(实际两条内容都在链上)
        inreplyto: 要回复的内容的 Trx ID, 如果提供, 内容将回复给这条指定内容

        返回值 {"trx_id": "string"}

        """
        obj = {"type": "Note"}

        if update_id:
            obj["id"] = update_id
        if content:
            obj["content"] = content
        if name:
            obj["name"] = name
        if images:
            obj["image"] = [ImgObj(img).__dict__ for img in images]  # Img(images).image_objs()
        if inreplyto:
            obj["inreplyto"] = {"trxid": inreplyto}

        if obj.get("content") == None and obj.get("image") == None:
            raise ValueError("need some content. images,text,or both.")

        return self._send(obj=obj)

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
        self._check_group_id()
        return self._get(f"{self.baseurl}/block/{self.group_id}/{block_id}")

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
        trxtype = content.get("type") or "other"
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

    def trx(self, trx_id: str = None):
        try:
            resp = self.content_trxs(trx_id=trx_id, num=1, is_include_starttrx=True)
            if len(resp) > 1:
                print("something is error", resp)
            elif len(resp) == 0:
                raise ValueError(f"nothing got. {resp} {trx_id} {self.group_id}")
            else:
                return resp[0]
        except Exception as e:
            print(e)
            return self._get(f"{self.baseurl}/trx/{self.group_id}/{trx_id}")
        return {"error": "nothing got."}

    def trxs_unique(self, trxs: List):
        """remove the duplicate trx from the trxs list"""
        new = {}
        for trx in trxs:
            if trx["TrxId"] not in new:
                new[trx["TrxId"]] = trx
        return [new[i] for i in new]

    def pubqueue(self):
        self._check_group_id()
        resp = self._get(f"{self.baseurl}/group/{self.group_id}/pubqueue")
        return resp.get("Data")
