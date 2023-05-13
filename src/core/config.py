from functools import lru_cache
from dotenv import load_dotenv
from fastapi_integration import FastApiConfig


class MyConfig(FastApiConfig):
    telegram_chat_id: str
    telegram_token: str


@lru_cache
def get_app_settings() -> FastApiConfig:
    load_dotenv()
    return MyConfig()
