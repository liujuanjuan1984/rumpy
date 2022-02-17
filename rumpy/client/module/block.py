import time
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True)
    BlockId = Column("block_id", String(64), unique=True, index=True)
    GroupId = Column("group_id", String(64))
    PrevBlockId = Column("prev_block_id", String(64))
    PreviousHash = Column("prev_hash", String(64))
    Trxs = Column("trxs", String)
    ProducerPubKey = Column("pubkey", String(64))
    Hash = Column("block_hash", String(64))
    Signature = Column("signature", String(128))
    TimeStamp = Column("timestamp", Integer)
    add_at = Column("add_at", Integer, default=int(round(time.time() * 1000000000)))

    def __repl__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "BlockId": self.BlockId,
            "GroupId": self.GroupId,
            "PrevBlockId": self.PrevBlockId,
            "PreviousHash": self.PreviousHash,
            "Trxs": self.Trxs,
            "ProducerPubKey": self.ProducerPubKey,
            "Hash": self.Hash,
            "Signature": self.Signature,
            "TimeStamp": self.TimeStamp,
        }
