import datetime
from sqlalchemy import Column, Integer, String, Boolean
from rumpy.modules.base import Base


class BotRss(Base):
    """the rss requests from users by comments; the finally results."""

    __tablename__ = "bot_rss"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    is_rss = Column(Boolean, default=None)
    user_group = Column(String(72), default=None)
    group_id = Column(String(36), default=None)
    user_id = Column(String(36), default=None)
    conversation_id = Column(String(36), default=None)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotComments(Base):
    """msgs from bot users which needs to be update rss or reply or send to rum groups."""

    __tablename__ = "bot_comments"
    id = Column(Integer, unique=True, primary_key=True, index=True)
    message_id = Column(String(36), unique=True)
    is_reply = Column(Boolean, default=None)
    is_to_rum = Column(Boolean, default=None)  # 是否转发到rum，不需要转发为None；需要转发但没发，设置为False，转发成功设为True
    quote_message_id = Column(String(36), default=None)
    conversation_id = Column(String(36), default=None)
    user_id = Column(String(36), default=None)
    text = Column(String, default=None)
    category = Column(String(36), default=None)
    timestamp = Column(String, default=None)  # 消息的发送时间
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotTrxs(Base):
    """trxs data from rum groups which waiting to be sent."""

    __tablename__ = "bot_trxs"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    trx_id = Column(String(36), unique=True)
    group_id = Column(String(36))
    text = Column(String)
    timestamp = Column(String)  # trx 的 timestamp
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotTrxsSent(Base):
    """the sent trxs data ."""

    __tablename__ = "bot_trxs_sent"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    trx_id = Column(String(36))
    group_id = Column(String(36))
    user_id = Column(String(36))
    conversation_id = Column(String(36))
    is_sent = Column(Boolean, default=None)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotRumProgress(Base):
    """the progress trx_id of rum groups"""

    __tablename__ = "bot_rum_progress"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    progress_type = Column(String(36))
    trx_id = Column(String(36), default=None)
    timestamp = Column(String)  # the timestamp of the trx
    group_id = Column(String(36))
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotAirDrops(Base):
    """the progress trx_id of rum groups"""

    __tablename__ = "bot_air_drops"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    mixin_id = Column(String(36))
    group_id = Column(String(36), default=None)
    pubkey = Column(String(36), default=None)
    num = Column(String, default=None)
    token = Column(String, default=None)
    memo = Column(String)
    is_sent = Column(Boolean, default=False)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)


class BotRumProfiles(Base):
    """the users profiles in rum groups."""

    __tablename__ = "bot_rum_profiles"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    group_id = Column(String(36))
    pubkey = Column(String(36))
    name = Column(String(36))
    wallet = Column(String, default=None)
    timestamp = Column(String)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)
