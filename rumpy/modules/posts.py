import time
from sqlalchemy import Column, Integer, String, Boolean
from rumpy.modules.base import Base


class Post(Base):
    """posts of content"""

    __tablename__ = "posts"

    pid = Column(Integer, primary_key=True)
    group_id = Column(String)
    trx_id = Column(String, index=True)  # 原始 trx_id，用于取内容
    trx_type = Column(String)  # 类型：origin，comment，reply （to comment or reply）
    refer_tid = Column(String)  # 相关的 trx_id，不是 origin 类型时有用
    like_num = Column(Integer, default=0)  # like 的计数
    dislike_num = Column(Integer, default=0)  # dislike 的计数
    add_at = Column(Integer, default=int(round(time.time() * 1000000000)))
    upd_at = Column(Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, post):
        super().__init__(**post)

    def __repr__(self):
        return f"Post({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        return {
            "pid": self.pid,
            "group_id": self.group_id,
            "trx_id": self.trx_id,
            "trx_type": self.trx_type,
            "refer_tid": self.refer_tid,
            "like_num": self.like_num,
            "dislike_num": self.dislike_num,
            "add_at": self.add_at,
            "upd_at": self.upd_at,
        }
