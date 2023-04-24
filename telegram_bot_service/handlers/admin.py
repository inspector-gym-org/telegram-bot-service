import json
from typing import cast

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..admin import notification_redis
from ..payment import PaymentStatus, update_payment
from ..training_plan import get_training_plan


async def update_payment_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    await query.answer()

    _, action, payment_id = query.data.split(";")

    if action == "accept":
        status = PaymentStatus.ACCEPTED
        message = "Підтверджено"
    elif action == "reject":
        status = PaymentStatus.REJECTED
        message = "Відхилено"

    payment = update_payment(payment_id, status)

    if not payment:
        return

    training_plan = get_training_plan(payment.items[0].training_plan_id)  # type: ignore

    await context.bot.send_message(
        chat_id=payment.user.telegram_id, text=training_plan.content_url
    )

    if raw_message_ids := notification_redis.get(payment_id):
        message_ids = cast(list[tuple[int, int]], json.loads(raw_message_ids.decode()))

        for chat_id, message_id in message_ids:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(message, callback_data="dummy")]]
                ),
            )

    notification_redis.delete(payment_id)


async def handle_dummy_inline_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if query := update.callback_query:
        await query.answer()
