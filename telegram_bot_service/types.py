from typing import Any, Callable

from telegram.ext import Application, CallbackContext, ExtBot, JobQueue

Translate = Callable[[str], str]
TelegramApplication = Application[
    ExtBot[None],
    CallbackContext[ExtBot[None], dict[Any, Any], dict[Any, Any], dict[Any, Any]],
    dict[Any, Any],
    dict[Any, Any],
    dict[Any, Any],
    JobQueue[
        CallbackContext[ExtBot[None], dict[Any, Any], dict[Any, Any], dict[Any, Any]]
    ],
]
