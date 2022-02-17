import time
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Trx(Base):
    __tablename__ = "trxs"

    id = Column(Integer, primary_key=True)
    TrxId = Column("trx_id", String(64), unique=True, index=True)
    Publisher = Column("pubkey", String(64))
    Content = Column("content", String)
    TypeUrl = Column("type_url", String(64))
    TimeStamp = Column("timestamp", Integer)
    add_at = Column("add_at", Integer, default=int(round(time.time() * 1000000000)))

    def __repl__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "TrxId": self.TrxId,
            "Publisher": self.Publisher,
            "Content": self.Content,
            "TypeUrl": self.TypeUrl,
            "TimeStamp": self.TimeStamp,
        }
