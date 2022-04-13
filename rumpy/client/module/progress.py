import time
from sqlalchemy import Column, Integer, String, Boolean
from rumpy.client.module.base import Base


class Progress(Base):
    """the content sync progress between db and group_chain."""

    __tablename__ = "progress"

    pid = Column(Integer, primary_key=True)
    group_id = Column(String)
    trx_id = Column(String, index=True)
    memo = Column(String)
    add_at = Column(Integer, default=int(round(time.time() * 1000000000)))
    upd_at = Column(Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, progress):
        super().__init__(**progress)
        self.trx_id = str(progress.get("trx_id"))
        self.memo = str(progress.get("memo"))

    def __repr__(self):
        return f"Progress({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        return {
            "pid": self.pid,
            "group_id": self.group_id,
            "trx_id": self.trx_id,
            "memo": self.memo,
            "add_at": self.add_at,
            "upd_at": self.upd_at,
        }
