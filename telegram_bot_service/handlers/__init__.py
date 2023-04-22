# mypy: disable-error-code="union-attr"

from typing import Callable

from telegram import KeyboardButton, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from ..language import get_translations
from ..user import User, authenticate_user
from .constants import MenuState
from .equipment_shop import send_equipment_shop_data
from .helpers import get_reply_keyboard, log_update_data
from .training_plan import (
    ask_sex,
    save_age_group,
    save_environment,
    save_frequency,
    save_goal,
    save_level,
    save_sex,
)


@log_update_data
@authenticate_user
@get_translations
async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    translate: Callable,
) -> MenuState:
    await update.effective_message.reply_text(
        translate("main_menu"),
        reply_markup=get_reply_keyboard(
            [
                KeyboardButton(
                    translate("individual_training_plan_button"),
                ),
                KeyboardButton(
                    translate("ready_made_plans_button"),
                ),
                KeyboardButton(translate("educational_plan_button")),
                KeyboardButton(translate("equipment_shop_button")),
            ],
            placeholder=translate("main_menu_placeholder"),
            one_time=False,
            keys_per_row=1,
        ),
    )

    return MenuState.MAIN_MENU


@log_update_data
@get_translations
async def handle_menu_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translate: Callable,
) -> MenuState:
    response = update.effective_message.text  # type: ignore[union-attr]

    if response == translate("individual_training_plan_button"):
        return await start_training_plan_survey(
            update=update, context=context, translate=translate
        )

    elif response == translate("ready_made_plans_button"):
        return MenuState.MAIN_MENU

    elif response == translate("educational_plan_button"):
        return MenuState.MAIN_MENU

    elif response == translate("equipment_shop_button"):
        return await send_equipment_shop_data(
            update=update, context=context, translate=translate
        )

    return MenuState.MAIN_MENU


@log_update_data
async def start_training_plan_survey(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("individual_training_plan_description"),
        reply_markup=get_reply_keyboard([KeyboardButton(translate("start_button"))]),
    )

    context.user_data["filters"] = {}  # type: ignore[index]
    return MenuState.INDIVIDUAL_PLAN_START


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
                # MenuState.PAYMENT_IMAGE: [MessageHandler(filters)],
            },
            fallbacks=[],
        ),
    )
