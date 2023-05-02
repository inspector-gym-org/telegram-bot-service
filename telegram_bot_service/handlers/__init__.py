from typing import Callable

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .admin import handle_dummy_inline_button, update_payment_button
from .constants import MenuState
from .equipment_shop import send_equipment_shop_data
from .helpers import get_translations, log_update_data
from .main_menu import send_main_menu
from .training_plan import (
    ask_sex,
    handle_health_condition,
    save_age_group,
    save_environment,
    save_frequency,
    save_goal,
    save_level,
    save_payment_screenshot,
    save_sex,
    start_training_plan_survey,
)


@log_update_data
@get_translations
async def handle_menu_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    response = update.effective_message.text  # type: ignore[union-attr]

    if response == translate("individual_training_plan_button"):
        return await start_training_plan_survey(
            update=update, context=context, translate=translate
        )

    elif response == translate("ready_made_plans_button"):
        await update.effective_message.reply_text(  # type: ignore[union-attr]
            translate("coming_soon")
        )
        return MenuState.MAIN_MENU

    elif response == translate("educational_plan_button"):
        await update.effective_message.reply_text(  # type: ignore[union-attr]
            translate("coming_soon")
        )
        return MenuState.MAIN_MENU

    elif response == translate("equipment_shop_button"):
        return await send_equipment_shop_data(
            update=update, context=context, translate=translate
        )

    return MenuState.MAIN_MENU


def register_handlers(telegram_application: Application) -> None:
    telegram_application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("start", send_main_menu),
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_menu_button),
            ],
            states={
                MenuState.MAIN_MENU: [
                    CommandHandler("start", send_main_menu),
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND), handle_menu_button
                    ),
                ],
                MenuState.INDIVIDUAL_PLAN_START: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), ask_sex)
                ],
                MenuState.SEX: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_sex)
                ],
                MenuState.AGE_GROUP: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_age_group)
                ],
                MenuState.HEALTH_CONDITION: [
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND), handle_health_condition
                    )
                ],
                MenuState.GOAL: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_goal)
                ],
                MenuState.ENVIRONMENT: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_environment)
                ],
                MenuState.LEVEL: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_level)
                ],
                MenuState.FREQUENCY: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), save_frequency)
                ],
                MenuState.PAYMENT_SCREENSHOT: [
                    MessageHandler(filters.ALL, save_payment_screenshot)
                ],
            },
            fallbacks=[CommandHandler("start", send_main_menu)],
        )
    )

    telegram_application.add_handler(
        CallbackQueryHandler(update_payment_button, pattern="^update_payment")
    )

    telegram_application.add_handler(
        CallbackQueryHandler(handle_dummy_inline_button, pattern="^dummy")
    )
