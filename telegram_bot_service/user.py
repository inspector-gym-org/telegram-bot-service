from functools import wraps
from typing import Any, Callable, Coroutine, cast

import requests
from fastapi import status
from pydantic import BaseModel
from telegram import Update
from telegram import User as TelegramUser

from .config import settings


class User(BaseModel):
    telegram_id: int

    first_name: str
    last_name: str | None
    username: str | None


def create_user(user: User) -> User | None:
    response = requests.post(
        url=settings.user_service_url + "/",
        timeout=settings.user_service_timeout,
        data=user.json(),
    )

    if response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        return None

    return User(**response.json())


def authenticate_user(
    wrapped: Callable[..., Any],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    def wrapper(update: Update, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        telegram_user = cast(TelegramUser, update.effective_user)
        user = User(
            telegram_id=telegram_user.id,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
        )

        kwargs["user"] = create_user(user)

        return wrapped(update=update, *args, **kwargs)

    return wrapper
