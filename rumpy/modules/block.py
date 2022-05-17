import time
from sqlalchemy import Column, Integer, String
from rumpy.modules.base import Base


class Block(Base):
    __tablename__ = "blocks"

    BlockId = Column("block_id", String(64), primary_key=True, unique=True, index=True)
    GroupId = Column("group_id", String(64))
    PrevBlockId = Column("prev_block_id", String(64))
    PreviousHash = Column("prev_hash", String(64))
    Trxs = Column("trxs", String)
    ProducerPubKey = Column("pubkey", String(64))
    Hash = Column("block_hash", String(64))
    Signature = Column("signature", String(128))
    TimeStamp = Column("timestamp", Integer)
    add_at = Column("add_at", Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, block):
        super().__init__(**block)
        # genesis_block don't have Trxs.
        self.Trxs = block.get("Trxs", [])

    def __repr__(self):
        return f"Block({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        block = {
            "BlockId": self.BlockId,
            "GroupId": self.GroupId,
            "PrevBlockId": self.PrevBlockId,
            "PreviousHash": self.PreviousHash,
            "Trxs": eval(self.Trxs),
            "ProducerPubKey": self.ProducerPubKey,
            "Hash": self.Hash,
            "Signature": self.Signature,
            "TimeStamp": self.TimeStamp,
        }
        # genesis_block don't have Trxs.
        if not block["Trxs"]:
            del block["Trxs"]
        return block
