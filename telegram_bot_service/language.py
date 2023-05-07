import gettext
from enum import Enum

from redis import Redis

from .config import settings
from .types import Translate

language_redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_language_db,
    decode_responses=True,
)


class Language(Enum):
    UKRAINIAN = "uk"
    ENGLISH = "en"


def get_user_translation_function(telegram_id: int) -> Translate:
    language = Language.UKRAINIAN

    if redis_value := language_redis.get(str(telegram_id)):
        language = Language(redis_value)

    return gettext.translation(
        "messages", "locale", languages=[language.value], fallback=True
    ).gettext
