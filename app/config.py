from .utils import SetBlacklist, RedisBlacklist
import os


class Config(object):
    DEBUG = False
    SECRET_KEY = 'os!zj92WqrxgdT66KLJe7BqnhgEEaM4i9h1.kN5MBYW-N42eI06SWB2FF878KiEUYF@V'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    HASH_METHOD = 'pbkdf2:sha512:20000'
    ACCESS_TOKEN_VALIDITY = 15  # minutes
    REFRESH_TOKEN_VALIDITY = 360  # minutes
    QR_SCALE = 5
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    BLACKLIST = SetBlacklist()


class ProductionConfig(Config):
    username = os.environ.get('MYSQL_USERNAME')
    password = os.environ.get('MYSQL_PASSWORD')
    hostname = os.environ.get('MYSQL_HOSTNAME')
    port = os.environ.get('MYSQL_PORT') or 3306
    database = os.environ.get('MYSQL_DATABASE')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8mb4'

    BLACKLIST = RedisBlacklist()
    # redis configuration to blacklist refresh tokens
    redis_host = os.environ.get('REDIS_HOSTNAME')
    redis_port = os.environ.get('REDIS_PORT') or 6379
    redis_password = os.environ.get('REDIS_PASSWORD') or ''
    redis_db = os.environ.get('REDIS_DATABASE')
    redis_base = f'{redis_host}:{redis_port}/{redis_db}'
    REDIS_URL = f'redis://:{redis_password}@{redis_base}' if redis_password else f'redis://{redis_base}'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root@localhost:3306/example?charset=utf8mb4'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
