import os

from pymongo import MongoClient


class DBClient:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = MongoClient(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT"))
            )
            cls.instance.db = cls.instance[os.getenv("DB_NAME")]
        return cls.instance
