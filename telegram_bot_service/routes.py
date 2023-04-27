from fastapi import APIRouter, Header, Response, status
from pydantic import BaseModel
from telegram import Update

from .config import settings
from .telegram import telegram_application


class TelegramWebhook(BaseModel):
    update_id: int

    message: dict | None
    edited_message: dict | None

    channel_post: dict | None
    edit_channel_post: dict | None

    inline_query: dict | None
    chosen_inline_result: dict | None
    callback_query: dict | None
    shipping_query: dict | None
    pre_checkout_query: dict | None

    poll: dict | None
    poll_answer: dict | None

    my_chat_member: dict | None
    chat_member: dict | None
    chat_join_request: dict | None


router = APIRouter(tags=["telegram", "webhook"])


@router.post("/")
async def handle_telegram_webhook(
    telegram_webhook: TelegramWebhook,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> Response:
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_token:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    update = Update.de_json(dict(telegram_webhook), telegram_application.bot)
    await telegram_application.process_update(update)

    return Response(status_code=status.HTTP_200_OK)
