import time
from sqlalchemy import Column, Integer, String, Boolean
from rumpy.client.module.base import Base


class Action(Base):
    """the actions of client."""

    __tablename__ = "actions"

    action_id = Column(Integer, primary_key=True)
    group_id = Column(String)
    trx_id = Column(String, index=True)
    func = Column(String)
    params = Column(String)
    is_onchain = Column(Boolean, default=False)
    add_at = Column(Integer, default=int(round(time.time() * 1000000000)))
    upd_at = Column(Integer, default=int(round(time.time() * 1000000000)))

    def __init__(self, action):
        super().__init__(**action)
        self.func = str(action.get("func"))
        self.params = str(action.get("params"))

    def __repr__(self):
        return f"Action({self.to_dict()})"

    def __str__(self):
        return f"{self.to_dict()}"

    def to_dict(self):
        return {
            "action_id": self.action_id,
            "group_id": self.group_id,
            "trx_id": self.trx_id,
            "func": self.func,
            "params": self.params,
            "is_onchain": self.is_onchain,
            "add_at": self.add_at,
            "upd_at": self.upd_at,
        }

    def onchain(self):
        self.is_onchain = True
        self.upd_at = int(round(time.time() * 1000000000))
        return self

    def act(self):
        return f"{self.func}(**{self.params})"
