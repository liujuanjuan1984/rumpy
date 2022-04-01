import time
from sqlalchemy import Column, Integer, String
from .base import Base


class Trx(Base):
    __tablename__ = "trxs"

    TrxId = Column(
        "trx_id", String(40), unique=True, primary_key=True, index=True
    )  # 36
    Publisher = Column("pubkey", String(56))  # 52
    Content = Column("content", String)
    TypeUrl = Column("type_url", String(32))  # 16
    TimeStamp = Column("timestamp", Integer)  # 19
    add_at = Column("add_at", Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, trx):
        super().__init__(**trx)
        self.Content = str(trx.get("Content") or {})

    def __repr__(self):
        return f"Trx({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        return {
            "TrxId": self.TrxId,
            "Publisher": self.Publisher,
            "Content": eval(self.Content),
            "TypeUrl": self.TypeUrl,
            "TimeStamp": self.TimeStamp,
        }
