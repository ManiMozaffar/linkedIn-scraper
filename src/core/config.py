from functools import lru_cache
from dotenv import load_dotenv

from fastapi_integration import FastApiConfig


@lru_cache
def get_app_settings() -> FastApiConfig:
    load_dotenv()
    return FastApiConfig()
