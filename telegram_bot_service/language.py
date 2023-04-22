import gettext
from enum import Enum
from functools import wraps
from typing import Any, Callable, Coroutine

from redis import Redis
from telegram import Update

from .config import settings

redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_language_db,
)


class Language(Enum):
    UKRAINIAN = "uk"
    ENGLISH = "en"


def get_translations(
    wrapped: Callable[..., Any],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    def wrapper(update: Update, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        language = Language.UKRAINIAN

        telegram_id = str(update.effective_user.id)  # type: ignore[union-attr]
        if redis_value := redis.get(telegram_id):
            language = Language(redis_value)

        translation = gettext.translation(
            "messages", "locale", languages=[language.value], fallback=True
        )

        kwargs["translate"] = translation.gettext
        return wrapped(update=update, *args, **kwargs)

    return wrapper
