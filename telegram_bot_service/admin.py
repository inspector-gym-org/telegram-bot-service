from redis import Redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message

from .config import settings
from .payment import Payment
from .training_plan import TrainingPlan

redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_admin_notification_db,
)


async def notify_individual_plan(
    media_message: Message, payment: Payment, training_plan: TrainingPlan
) -> None:
    user = media_message.from_user

    caption = (
        "Оплата індивідуального плану:\n"
        f"План: {training_plan.url}\n"
        f"Сума: *{training_plan.price} грн*\n"
        f"Користувач: @{user.username}"
        if user and user.username
        else "Користувач не має нікнейму"
    )

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "OK", callback_data=f"accept_payment;{payment.id}"
                ),
                InlineKeyboardButton(
                    "NOT OK", callback_data=f"reject_payment;{payment.id}"
                ),
            ]
        ]
    )

    message_ids = []

    for admin_chat_id in settings.bot_admin_chat_ids:
        message = await media_message.copy(
            chat_id=admin_chat_id, caption=caption, reply_markup=reply_markup
        )
        message_ids.append(message.message_id)
