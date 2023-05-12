from sqlalchemy.orm import declarative_base
from loguru import logger
import redis
from fastapi_integration.db import SqlEngine

from core.config import get_app_settings


class RedisDatabase:
    def __init__(self) -> None:
        global_settings = get_app_settings()
        self.redis_pool = redis.ConnectionPool(
            host=global_settings.redis_url.host,
            port=global_settings.redis_url.port,
            db=int(global_settings.redis_url.path[1:]),
            username=global_settings.redis_url.user,
            password=global_settings.redis_url.password,
            max_connections=global_settings.redis_max_connections,
        )

    def test_connection(self):
        logger.info("Connecting to Redis")
        self.get_connection().set('test', 'test', ex=1)
        logger.info("Connection established")

    def get_connection(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.redis_pool)


SQL_ENGINE = SqlEngine(get_app_settings())
REDIS_DB = RedisDatabase()
Base = declarative_base()


def get_redis_db():
    return REDIS_DB.get_connection
