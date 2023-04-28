import json
from logging import getLogger
from typing import cast

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from ..admin import notification_redis
from ..language import get_user_translation_function
from ..payment import PaymentStatus, update_payment
from ..training_plan import get_training_plan
from .helpers import log_update_data

logger = getLogger("service")

ACTION_TO_STATUS = {"accept": PaymentStatus.ACCEPTED, "reject": PaymentStatus.REJECTED}


@log_update_data
async def update_payment_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    await query.answer()

    _, action, payment_id = query.data.split(";")

    status = ACTION_TO_STATUS[action]
    payment = update_payment(payment_id, status)

    if not payment:
        return

    user_id = payment.user.telegram_id
    translate = get_user_translation_function(user_id)

    if status == PaymentStatus.ACCEPTED:
        message = "Підтверджено"
        training_plan = get_training_plan(
            payment.items[0].training_plan_id,  # type: ignore
        )

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=translate("training_plan_payment_accepted"),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                translate("training_plan_url"),
                                url=training_plan.content_url,
                            )
                        ]
                    ]
                ),
            )

            logger.debug(f"Sent payment {payment.id} confirmation to {user_id}")

        except TelegramError as exc:
            logger.error(
                f"Unable to send payment {payment.id} confirmation to {user_id}",
                exc_info=exc,
            )

    elif status == PaymentStatus.REJECTED:
        message = "Відхилено"

        try:
            await context.bot.send_message(
                chat_id=payment.user.telegram_id,
                text=translate("training_plan_payment_rejected"),
            )

            logger.debug(f"Sent payment {payment.id} rejection to {user_id}")

        except TelegramError as exc:
            logger.error(
                f"Unable to send payment {payment.id} rejection to {user_id}",
                exc_info=exc,
            )

    if raw_message_ids := notification_redis.get(payment_id):
        message_ids = cast(list[tuple[int, int]], json.loads(raw_message_ids.decode()))

        for chat_id, message_id in message_ids:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(message, callback_data="dummy")]]
                    ),
                )

                logger.debug(f"Updated payment {payment.id} message in chat {chat_id}")

            except TelegramError as exc:
                logger.error(
                    f"Unable to update payment {payment.id} message in chat {chat_id}",
                    exc_info=exc,
                )

    notification_redis.delete(payment_id)


async def handle_dummy_inline_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if query := update.callback_query:
        await query.answer()
