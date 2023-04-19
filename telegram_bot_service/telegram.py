from telegram.ext import Application

from .config import settings

telegram_application = (
    Application.builder()
    .token(settings.telegram_bot_token)
    .concurrent_updates(True)
    .build()
)
