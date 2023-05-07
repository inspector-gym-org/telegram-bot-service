# pyright: reportOptionalMemberAccess=false

from functools import wraps
from logging import getLogger
from typing import Any, Callable, Coroutine, cast

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram import User as TelegramUser
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from ..config import settings
from ..language import get_user_translation_function
from ..user import User, create_user

logger = getLogger("service")


def log_update_data(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, Any]:
        logger.debug(f"{wrapped.__name__} update: {update}")
        logger.debug(f"{wrapped.__name__} user_data: {context.user_data}")

        result = await wrapped(update=update, context=context, *args, **kwargs)

        logger.debug(f"{wrapped.__name__} output: {result}")

        return result

    return wrapper


def authenticate_user(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, Any]:
        telegram_user = cast(TelegramUser, update.effective_user)

        user = User(
            telegram_id=telegram_user.id,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
        )

        kwargs["user"] = await create_user(user)

        return await wrapped(update=update, *args, **kwargs)

    return wrapper


def require_admin(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, Any]:
        user_id = update.effective_user.id
        if user_id not in settings.bot_admin_chat_ids:
            raise PermissionError(f"User {user_id} is not admin")

        return await wrapped(update=update, *args, **kwargs)

    return wrapper


def send_typing_action(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, Any]:
        await update.effective_message.reply_chat_action(ChatAction.TYPING)

        return await wrapped(update=update, *args, **kwargs)

    return wrapper


def get_translations(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, Any]:
        kwargs["translate"] = get_user_translation_function(update.effective_user.id)

        return await wrapped(update=update, *args, **kwargs)

    return wrapper


def get_reply_keyboard(
    keys: list[KeyboardButton],
    keys_per_row: int = 2,
    resize: bool = True,
    one_time: bool = True,
    placeholder: str = "",
    additional_row: list[KeyboardButton] | None = None,
) -> ReplyKeyboardMarkup:
    keyboard = [
        [keys[i + j] for j in range(keys_per_row) if i + j < len(keys)]
        for i in range(0, len(keys), keys_per_row)
    ]

    if additional_row:
        keyboard.append(additional_row)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize,
        one_time_keyboard=one_time,
        input_field_placeholder=placeholder,
    )
