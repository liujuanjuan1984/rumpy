from dataclasses import dataclass
import inspect
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import urllib3

urllib3.disable_warnings()
from . import api
from .api.base import BaseAPI
from .module.base import Base


@dataclass
class RumClientParams:
    """
    :param appid, str, Rum 客户端标识，自定义，随便写
    :param port, int, Rum 服务 端口号
    :param host,str, Rum 服务 host，通常是 127.0.0.1
    :param crtfile, str, Rum 的 server.crt 文件的绝对路径

    {
        "port":8002,
        "host":"127.0.0.1",
        "appid":"peer"
        "crtfile":"",
    }
    """

    port: int
    crtfile: str
    host: str = "127.0.0.1"
    appid: str = "peer"
    jwt_token: str = None
    dbname: str = "test_db"


def _is_api_endpoint(obj):
    return isinstance(obj, BaseAPI)


class BaseDB:
    def __init__(self, dbname, echo=True):
        # 创建数据库
        engine = create_engine(f"sqlite:///{dbname}.db", echo=echo)
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


class RumClient:
    _group_id = None
    group = api.Group()
    node = api.Node()
    config = api.GroupConfig()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, **kwargs):
        cp = RumClientParams(**kwargs)
        requests.adapters.DEFAULT_RETRIES = 5
        self.appid = cp.appid
        self._session = requests.Session()
        self._session.verify = cp.crtfile
        self._session.keep_alive = False

        self._session.headers.update(
            {
                "USER-AGENT": "python.api",
                "Content-Type": "application/json",
            }
        )
        if cp.jwt_token:
            self._session.headers.update({"Authorization": f"Bearer {cp.jwt_token}"})
        self.baseurl = f"https://{cp.host}:{cp.port}/api/v1"
        self.db = BaseDB(cp.dbname)

    def _request(self, method, url, relay={}):
        resp = self._session.request(method=method, url=url, json=relay)
        return resp.json()

    def get(self, url, relay={}):
        return self._request("get", url, relay)

    def post(self, url, relay={}):
        return self._request("post", url, relay)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id

    @group_id.deleter
    def group_id(self):
        del self._group_id
