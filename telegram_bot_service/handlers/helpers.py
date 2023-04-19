# mypy: disable-error-code="union-attr"

from functools import wraps
from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction


def send_typing_action(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(update: Update, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        await update.effective_message.reply_chat_action(ChatAction.TYPING)
        return await wrapped(update, *args, **kwargs)

    return wrapper


def log_update_data(
    wrapped: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(wrapped)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ) -> Coroutine[Any, Any, Any]:
        print(f"{wrapped.__name__} update: {update}")
        print(f"{wrapped.__name__} user_data: {context.user_data}")

        result = await wrapped(update, context, *args, **kwargs)

        print(f"{wrapped.__name__} output: {result}")

        return result

    return wrapper
