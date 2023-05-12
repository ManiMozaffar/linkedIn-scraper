import logging

import uvicorn
from fastapi_integration import FastAPIExtended, FastApiConfig

from core.routes import router
from db import Base, SQL_ENGINE


app = FastAPIExtended(
    features=[
        FastApiConfig,
    ],
    db_engine=SQL_ENGINE,
    routers=[
        router
    ],
    base=Base
)


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
