from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
import logging
import uvicorn

from core.handlers import http_error_handler, http422_error_handler
from core.config import get_app_settings
from core.events import create_start_app_handler, create_stop_app_handler
from core.routes import router


settings = get_app_settings()
settings.configure_logging()


def get_application() -> FastAPI:
    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(),
    )
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(
        RequestValidationError, http422_error_handler
    )
    application.include_router(router, prefix=settings.api_prefix)
    return application


app = get_application()


def run_application():
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            workers=1,
        )
    except Exception as e:
        logging.error("An error occurred while running the application")
        logging.exception(e)


if __name__ == "__main__":
    run_application()
