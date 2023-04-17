from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger
import redis

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


engine = create_async_engine(
    get_app_settings().database_url,
    future=True,
    echo=False,
)


async def get_db() -> AsyncGenerator:
    AsyncSessionFactory = sessionmaker(
        engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
    )
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session


REDIS_DB = RedisDatabase()


def get_redis_db():
    return REDIS_DB.get_connection


def get_base():
    return declarative_base()


Base = get_base()
