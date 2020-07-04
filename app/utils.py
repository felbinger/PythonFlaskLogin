from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class RedisBlacklist:
    def __init__(self) -> "RedisBlacklist":
        self.blacklist = FlaskRedis()

    def add(self, token: str):
        self.blacklist.sadd('blacklist', token)
        pass

    def check(self, token: str) -> bool:
        return self.blacklist.smembers(token)


class SetBlacklist:
    def __init__(self):
        self.blacklist = set()

    def add(self, token: str):
        self.blacklist.add(token)

    def check(self, token: str) -> bool:
        return token in self.blacklist
