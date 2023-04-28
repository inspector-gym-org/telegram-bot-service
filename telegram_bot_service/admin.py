import json
from logging import getLogger
from typing import cast

from redis import Redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, User
from telegram.error import TelegramError

from .config import settings
from .payment import Payment, PaymentStatus, update_payment
from .training_plan import TrainingPlan

logger = getLogger("service")

notification_redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_admin_notification_db,
)


async def notify_individual_plan(
    media_message: Message, payment: Payment, training_plan: TrainingPlan
) -> None:
    user = cast(User, media_message.from_user)

    caption = (
        "*Оплата індивідуального плану*\n"
        f"*Сума:* _{training_plan.price:.2f} грн_\n"
        f"*План:* [Notion-сторінка]({training_plan.url})\n"
        f"*Користувач:* [Telegram-профіль](tg://user?id={user.id})"
    )

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "OK", callback_data=f"update_payment;accept;{payment.id}"
                ),
                InlineKeyboardButton(
                    "не OK", callback_data=f"update_payment;reject;{payment.id}"
                ),
            ]
        ]
    )

    message_ids = []

    for admin_chat_id in settings.bot_admin_chat_ids:
        try:
            message = await media_message.copy(
                chat_id=admin_chat_id, caption=caption, reply_markup=reply_markup
            )
            message_ids.append((admin_chat_id, message.message_id))

            logger.debug(f"Sent payment {payment.id} notification to {admin_chat_id}")

        except TelegramError as exc:
            logger.error(
                f"Unable to send notification to {admin_chat_id}", exc_info=exc
            )

    notification_redis.set(str(payment.id), json.dumps(message_ids))

    update_payment(
        payment_id=payment.id,  # type: ignore
        new_status=PaymentStatus.PROCESSING,
    )
