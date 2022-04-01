from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from rumpy.client.module.base import Base


class BaseDB:
    def __init__(self, dbname, echo, reset):
        # 创建数据库
        engine = create_engine(f"sqlite:///{dbname}.db", echo=echo)
        if reset:
            Base.metadata.drop_all(engine)
        # 创建表
        Base.metadata.create_all(engine)
        # 创建会话
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def __commit(self):
        """Commits the current db.session, does rollback on failure."""
        from sqlalchemy.exc import IntegrityError

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def save(self, obj):
        """Adds this model to the db (through db.session)"""
        self.session.add(obj)
        self.__commit()
        return self
