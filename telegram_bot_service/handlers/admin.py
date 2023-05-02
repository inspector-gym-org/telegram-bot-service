from logging import getLogger

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from ..admin import notification_redis
from ..language import get_user_translation_function
from ..payment import PaymentStatus, update_payment
from ..training_plan import get_training_plan
from .helpers import log_update_data

logger = getLogger("service")

ACTION_TO_STATUS = {
    "accept": (PaymentStatus.ACCEPTED, "Підтверджено"),
    "reject": (PaymentStatus.REJECTED, "Відхилено"),
}


@log_update_data
async def update_payment_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    await query.answer()

    _, action, payment_id = query.data.split(";")

    status, message = ACTION_TO_STATUS[action]
    payment = await update_payment(payment_id, status)

    if not payment:
        return

    user_id = payment.user.telegram_id
    translate = get_user_translation_function(user_id)

    if status == PaymentStatus.ACCEPTED:
        training_plan = await get_training_plan(
            payment.items[0].training_plan_id  # type: ignore[arg-type]
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

            logger.debug(f"Sent payment {payment_id} confirmation to {user_id}")

        except TelegramError as exc:
            logger.error(
                f"Unable to send payment {payment_id} confirmation to {user_id}",
                exc_info=exc,
            )
            await update.effective_message.reply_text(  # type: ignore[union-attr]
                "Помилка відправки повідомлення про підтвердження користувачу",
                quote=True,
            )
            return

    elif status == PaymentStatus.REJECTED:
        try:
            await context.bot.send_message(
                chat_id=user_id, text=translate("training_plan_payment_rejected")
            )

            logger.debug(f"Sent payment {payment_id} rejection to {user_id}")

        except TelegramError as exc:
            logger.error(
                f"Unable to send payment {payment_id} rejection to {user_id}",
                exc_info=exc,
            )
            await update.effective_message.reply_text(  # type: ignore[union-attr]
                "Помилка відправки повідомлення про відмову користувачу", quote=True
            )

    if raw_message_ids := notification_redis.hgetall(payment_id):
        for chat_id, message_id in raw_message_ids.items():
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=int(message_id),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(message, callback_data="dummy")]]
                    ),
                )

                logger.debug(f"Updated payment {payment_id} message in chat {chat_id}")

            except TelegramError as exc:
                logger.error(
                    f"Unable to update payment {payment_id} message in chat {chat_id}",
                    exc_info=exc,
                )

        notification_redis.hdel(payment_id, *raw_message_ids.keys())


async def handle_dummy_inline_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if query := update.callback_query:
        await query.answer()
