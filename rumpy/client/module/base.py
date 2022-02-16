from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
from . import Block, Trx


def init_db(dbname="test_db", echo=False):
    # 创建数据库
    engine = create_engine(f"sqlite:///{dbname}", echo=echo)
    # 创建表
    Base.metadata.create_all(engine)
    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
