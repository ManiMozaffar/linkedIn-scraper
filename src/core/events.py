from typing import Callable
from loguru import logger
from core.settings.app import AppSettings
from db import engine, AsyncSession
from services import create_all_tables

app_settings = AppSettings()


def create_start_app_handler() -> Callable:
    async def start_app() -> None:
        logger.info("Connecting to  PostgreSQL")
        async with AsyncSession(engine) as session:
            async with session.begin():
                pass

        create_tables = create_all_tables()
        logger.info("Connection established")
        # get_redis_db().test_connection()
        await create_tables
    return start_app


def create_stop_app_handler() -> Callable:
    async def stop_app() -> None:
        async with engine.connect() as conn:
            await conn.close()
            await engine.dispose()
    return stop_app
