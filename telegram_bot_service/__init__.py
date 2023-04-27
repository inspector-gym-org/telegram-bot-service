from contextlib import asynccontextmanager
from logging.config import dictConfig
from typing import AsyncGenerator

from fastapi import FastAPI

from .handlers import register_handlers
from .logging import LogConfig
from .routes import router
from .telegram import telegram_application


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await telegram_application.initialize()
    yield
    await telegram_application.shutdown()


def build_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    dictConfig(LogConfig().dict())

    register_handlers(telegram_application)

    return app
