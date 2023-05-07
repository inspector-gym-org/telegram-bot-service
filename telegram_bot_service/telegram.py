from telegram.constants import ParseMode
from telegram.ext import Application, Defaults

from .config import settings
from .types import TelegramApplication

defaults = Defaults(parse_mode=ParseMode.MARKDOWN)

telegram_application: TelegramApplication = (
    Application.builder()
    .token(settings.telegram_bot_token)
    .concurrent_updates(True)
    .defaults(defaults)
    .build()
)
