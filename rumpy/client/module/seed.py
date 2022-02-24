import time
from sqlalchemy import Column, Integer, String
from .base import Base


class Seed(Base):
    __tablename__ = "seeds"

    group_id = Column(String, primary_key=True, unique=True, index=True)
    group_name = Column(String)
    owner_pubkey = Column(String)
    consensus_type = Column(String)
    encryption_type = Column(String)
    cipher_key = Column(String)
    app_key = Column(String)
    signature = Column(String)
    genesis_block = Column(String)
    add_at = Column("add_at", Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, seed):
        super().__init__(**seed)
        self.genesis_block = str(seed["genesis_block"])

    def __repr__(self):
        return f"Seed({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        return {
            "genesis_block": eval(self.genesis_block),
            "group_id": self.group_id,
            "group_name": self.group_name,
            "owner_pubkey": self.owner_pubkey,
            "consensus_type": self.consensus_type,
            "encryption_type": self.encryption_type,
            "cipher_key": self.cipher_key,
            "app_key": self.app_key,
            "signature": self.signature,
        }
