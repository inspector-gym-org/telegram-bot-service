# mypy: disable-error-code="arg-type,index,union-attr"

from enum import IntEnum, auto
from typing import Callable

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from ..language import get_translations
from ..training_plan import get_existing_property_values
from ..training_plan.filters import (
    Environment,
    Frequency,
    Goal,
    Level,
    Sex,
    get_filter_reply_keyboard,
    verify_filter_reply_keyboard_choice,
)
from ..user import User, authenticate_user
from .helpers import log_update_data, send_typing_action


class MenuState(IntEnum):
    MAIN_MENU = auto()

    INDIVIDUAL_PLAN_START = auto()
    SEX = auto()
    AGE_GROUP = auto()
    GOAL = auto()
    ENVIRONMENT = auto()
    LEVEL = auto()
    FREQUENCY = auto()

    PAYMENT_IMAGE = auto()


class AgeGroup(IntEnum):
    UNDER_20 = 20
    UNDER_30 = 30
    UNDER_40 = 40
    ABOVE_40 = 41


@log_update_data
@authenticate_user
@get_translations
async def get_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    translate: Callable,
) -> MenuState:
    reply_markup = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    translate("individual_training_plan_button"),
                ),
            ],
            [
                KeyboardButton(
                    translate("ready_made_plans_button"),
                ),
            ],
            [
                KeyboardButton(translate("educational_plan_button")),
                KeyboardButton(translate("equipment_shop_button")),
            ],
        ],
        resize_keyboard=True,
    )

    await update.effective_message.reply_text(
        translate("start_menu"), reply_markup=reply_markup
    )

    return MenuState.MAIN_MENU


@log_update_data
@get_translations
async def handle_menu_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translate: Callable,
) -> MenuState:
    response = update.effective_message.text

    if response == translate("individual_training_plan_button"):
        return await start_individual_training_plan(update, context, translate)

    elif response == translate("ready_made_plans_button"):
        return MenuState.MAIN_MENU

    elif response == translate("educational_plan_button"):
        return MenuState.MAIN_MENU

    elif response == translate("equipment_shop_button"):
        return await send_equipment_shop_data(update, context, translate)

    return MenuState.MAIN_MENU


@log_update_data
@send_typing_action
async def send_equipment_shop_data(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translate: Callable,
) -> MenuState:
    await update.effective_message.reply_chat_action(ChatAction.TYPING)

    await update.effective_message.reply_text(
        translate("equipment_shop_description"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        translate("Наш магазин на olx.ua"),
                        url="https://www.olx.ua/uk/list/user/LX9Mb/",
                    )
                ],
            ]
        ),
    )

    return MenuState.MAIN_MENU


@log_update_data
async def start_individual_training_plan(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("individual_training_plan_description"),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(translate("start_button"))]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    context.user_data["filters"] = {}
    return MenuState.INDIVIDUAL_PLAN_START


@log_update_data
@get_translations
async def ask_sex(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translate: Callable,
) -> MenuState:
    available_values = get_existing_property_values(
        filter_enum=Sex, **context.user_data["filters"]
    )

    await update.effective_message.reply_text(
        translate("sex_description"),
        reply_markup=get_filter_reply_keyboard(translate, Sex, available_values),
    )

    return MenuState.SEX


@log_update_data
@send_typing_action
@get_translations
async def save_sex(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    if result := verify_filter_reply_keyboard_choice(
        translate, Sex, update.effective_message.text
    ):
        context.user_data["filters"]["sex"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.SEX

    return await ask_age_group(update, context, translate)


@log_update_data
@send_typing_action
async def ask_age_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("age_group_description"),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(translate("age_group_under_20_button"))],
                [KeyboardButton(translate("age_group_under_30_button"))],
                [KeyboardButton(translate("age_group_under_40_button"))],
                [KeyboardButton(translate("age_group_above_40_button"))],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return MenuState.AGE_GROUP


@log_update_data
@get_translations
async def save_age_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    response = update.effective_message.text

    if response == translate("age_group_under_20_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_20

    elif response == translate("age_group_under_30_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_30

    elif response == translate("age_group_under_40_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_40

    elif response == translate("age_group_above_40_button"):
        context.user_data["age_group"] = AgeGroup.ABOVE_40

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.AGE_GROUP

    return await ask_goal(update, context, translate)


@log_update_data
@send_typing_action
async def ask_goal(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    available_values = get_existing_property_values(
        filter_enum=Goal, **context.user_data["filters"]
    )

    await update.effective_message.reply_text(
        translate("goal_description"),
        reply_markup=get_filter_reply_keyboard(translate, Goal, available_values),
    )

    return MenuState.GOAL


@log_update_data
@get_translations
async def save_goal(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    if result := verify_filter_reply_keyboard_choice(
        translate, Goal, update.effective_message.text
    ):
        context.user_data["filters"]["goal"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.GOAL

    return await ask_environment(update, context, translate)


@log_update_data
@send_typing_action
async def ask_environment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    available_values = get_existing_property_values(
        filter_enum=Environment, **context.user_data["filters"]
    )

    await update.effective_message.reply_text(
        translate("environment_description"),
        reply_markup=get_filter_reply_keyboard(
            translate, Environment, available_values
        ),
    )

    return MenuState.ENVIRONMENT


@log_update_data
@send_typing_action
@get_translations
async def save_environment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    if result := verify_filter_reply_keyboard_choice(
        translate, Environment, update.effective_message.text
    ):
        context.user_data["filters"]["environment"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.ENVIRONMENT

    if context.user_data["filters"]["environment"] == Environment.HOUSE_AND_STREET:
        await send_equipment_shop_data(update, context, translate)

    return await ask_level(update, context, translate)


@log_update_data
@send_typing_action
async def ask_level(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    available_values = get_existing_property_values(
        filter_enum=Level, **context.user_data["filters"]
    )

    await update.effective_message.reply_text(
        translate("level_description"),
        reply_markup=get_filter_reply_keyboard(translate, Level, available_values),
    )

    return MenuState.LEVEL


@log_update_data
@get_translations
async def save_level(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    if result := verify_filter_reply_keyboard_choice(
        translate, Level, update.effective_message.text
    ):
        context.user_data["filters"]["level"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.LEVEL

    return await ask_frequency(update, context, translate)


@log_update_data
@send_typing_action
async def ask_frequency(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    available_values = get_existing_property_values(
        filter_enum=Frequency, **context.user_data["filters"]
    )

    if len(available_values) == 1:
        context.user_data["filters"]["frequency"] = available_values[0]
        return await send_payment_data(update, context, translate)

    await update.effective_message.reply_text(
        translate("frequency_description"),
        reply_markup=get_filter_reply_keyboard(translate, Frequency, available_values),
    )

    return MenuState.FREQUENCY


@log_update_data
@get_translations
async def save_frequency(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    if result := verify_filter_reply_keyboard_choice(
        translate, Frequency, update.effective_message.text
    ):
        context.user_data["filters"]["frequency"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.FREQUENCY

    return await send_payment_data(update, context, translate)


@log_update_data
async def send_payment_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("payment_data"), reply_markup=ReplyKeyboardRemove()
    )

    return MenuState.PAYMENT_IMAGE


def register_handlers(telegram_application: Application) -> None:
    telegram_application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("start", get_menu),
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_menu_button),
            ],
            states={
                MenuState.MAIN_MENU: [
                    CommandHandler("start", get_menu),
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
            },
            fallbacks=[],
        ),
    )
