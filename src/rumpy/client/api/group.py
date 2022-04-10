from typing import List, Dict, Any
from rumpy.client.api.base import BaseAPI
from rumpy.client.api.data import *
from munch import Munch


class Group(BaseAPI):
    def create(self,
               group_name,
               consensus_type="poa",
               encryption_type="public",
               app_key="group_timeline"):
        """创建一个组
        
        group_name: 组名
        consensus_type: 共识类型, "poa", "pos", "pow", 当前仅支持 "poa"
        encryption_type: 加密类型, "public" 公开, "private" 私有
        app_key: 应用标识, 自定义, 目前 rum-app 支持 "group_timeline", "group_post", "group_note"
        
        创建成功, 返回值是一个组的种子, 通过它其他人可加入组
        """
        data = Munch(group_name=group_name,
                     consensus_type=consensus_type,
                     encryption_type=encryption_type,
                     app_key=app_key)
        return self._post(f"{self.baseurl}/group", data)

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
            return self._post(f"{self.baseurl}/group/leave",
                              {"group_id": self.group_id})

    def clear(self):
        """clear data of a group"""
        self._check_group_id()
        return self._post(f"{self.baseurl}/group/clear",
                          {"group_id": self.group_id})

    def startsync(self):
        if self.is_joined():
            return self._post(
                f"{self.baseurl}/group/{self.group_id}/startsync")

    def content(self) -> List:
        """get the content trxs of a group,return the list of the trxs data."""
        if self.is_joined():
            return self._get(
                f"{self.baseurl}/group/{self.group_id}/content") or []

    def content_trxs(self,
                     reverse=False,
                     trx_id=None,
                     num=None,
                     includestarttrx=False) -> List:
        """按条件获取某个组的内容并去重返回
        
        reverse: 默认按顺序获取, 如果是 True, 从最新的内容开始获取
        trx_id: 某条内容的 Trx ID, 如果提供, 从该条之后(不包含)获取
        num: 要获取内容条数, 默认获取最前面的 20 条内容
        includestarttrx: 如果是 True, 获取内容包含 Trx ID 这条内容
        """
        if not self.is_joined():
            return []

        url = self.baseurl.replace("api", "app/api")

        reverse = "&reverse=true" if reverse else ""
        trx_id = f"&starttrx={trx_id}" if trx_id else ""
        num = f"&num={num}" if num else ""
        includestarttrx = "&includestarttrx=true" if includestarttrx else ""

        apiurl = f"{url}/group/{self.group_id}/content?{reverse}{trx_id}{num}{includestarttrx}"
        trxs = self._post(apiurl) or []
        return self.trxs_unique(trxs)

    def _send(self, obj: Dict, sendtype="Add") -> Dict:
        """发送对象到一个组
        
        obj: 要发送的对象
        sendtype: 发送类型, "Add"(发送内容), "Like"(点赞), "Dislike"(点踩)
        返回值 {"trx_id": "string"}
        """
        if self.is_joined():
            data = Munch(type=sendtype,
                         object=obj,
                         target={
                             "id": self.group_id,
                             "type": "Group"
                         })

            return self._post(f"{self.baseurl}/group/content", data)

    def like(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Like")

    def dislike(self, trx_id: str) -> Dict:
        return self._send(obj={"id": trx_id}, sendtype="Dislike")

    def send_note(self, content=None, name=None, images=None, trx_id=None):
        """发送/回复内容到一个组(仅图片, 仅文本, 或两者都有)
        
        content: 要发送的文本内容
        name: 内容标题, 例如 rum-app 论坛模板必须提供的文章标题
        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
            content 和 images 必须至少一个不是 None
        trx_id: 要回复的内容的 Trx ID, 如果提供, 内容将回复给这条指定内容

        返回值 {"trx_id": "string"}
        """
        if images is not None:
            images = Img(images).image_objs()
        if content is None and images is None:
            raise ValueError("need some content. images,text,or both.")
        obj = Munch(type="Note", content=content, name=name, image=images)
        if trx_id is not None:
            obj.inreplyto = {"trxid": trx_id}
        return self._send(obj)

    def reply(self, trx_id: str, content=None, images=None):
        """回复某条内容(仅图片, 仅文本, 或两者都有)
        
        trx_id: 要回复的内容的 Trx ID
        content: 用于回复的文本内容
        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
            content 和 images 必须至少一个不是 None
        """
        return self.send_note(content, images=images, trx_id=trx_id)

    def send_text(self, content: str, name: str = None):
        """post text cotnent to group
        
        content: 要发送的文本内容
        name: 内容标题, 例如 rum-app 论坛模板必须提供的文章标题
        """
        return self.send_note(content=content, name=name)

    def send_img(self, images):
        """post images to group, up to 4
        
        images: 一张或多张(最多4张)图片的路径, 一张是字符串, 多张则是它们组成的列表
        """
        return self.send_note(images=images)

    def block(self, block_id: str = None):
        """get the info of a block in a group"""
        self._check_group_id()
        return self._get(f"{self.baseurl}/block/{self.group_id}/{block_id}")

    def is_owner(self) -> bool:
        """return True if I create this group else False"""
        ginfo = self.info()
        if isinstance(ginfo,
                      GroupInfo) and ginfo.owner_pubkey == ginfo.user_pubkey:
            return True
        return False

    def all_content_trxs(self, trx_id=None):
        """get all the trxs of content started from trx_id"""
        trxs = []
        checked_trxids = []
        while True:
            if trx_id in checked_trxids:
                break
            else:
                checked_trxids.append(trx_id)
            newtrxs = self.content_trxs(trx_id=trx_id, num=100)
            if len(newtrxs) == 0:
                break
            trxs.extend(newtrxs)
            trx_id = self.last_trx_id(trx_id, newtrxs)
        return trxs

    def last_trx_id(self, trx_id, trxs):
        """get the last-trx_id of trxs which if different from given trx_id"""
        for i in range(-1, -1 * len(trxs), -1):
            tid = trxs[i]["TrxId"]
            if tid != trx_id:
                return tid
        return trx_id

    def trxs_by(self, pubkeys, trx_id=None):
        """获取从指定的 Trx 之后, 指定用户产生的所有 Trxs
        
        pubkeys: 指定用户的用户公钥组成的列表
        trx_id: 指定 Trx 的 ID
        """
        trxs = self.all_content_trxs(trx_id)
        trxs_by = [i for i in trxs if i["Publisher"] in pubkeys]
        return trxs_by

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
            resp = self.content_trxs(trx_id=trx_id,
                                     num=1,
                                     includestarttrx=True)
            if len(resp) > 1:
                print("somthing is error", resp)
            elif len(resp) == 0:
                raise ValueError(
                    f"nothing got. {resp} {trx_id} {self.group_id}")
            else:
                return resp[0]
        except Exception as e:
            print(e)
            return self._get(f"{self.baseurl}/trx/{self.group_id}/{trx_id}")
        return {"error": "nothing got."}

    def trxs_unique(self, trxs):
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
