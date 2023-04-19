# mypy: disable-error-code="arg-type,index,union-attr"

from enum import Enum
from typing import Callable, cast

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from ..language import get_translations
from ..training_plan import (
    Environment,
    FilterEnum,
    Frequency,
    Goal,
    Level,
    Sex,
    get_existing_property_values,
)
from .constants import MenuState
from .helpers import get_reply_keyboard, log_update_data, send_typing_action


def get_button_string_id_from_filter_enum(
    filter_enum: FilterEnum,
) -> str:
    return (
        f"{filter_enum.__class__.__name__.lower()}_"
        f"{filter_enum.name.lower()}_button"
    )


def get_filter_reply_keyboard(
    translate: Callable,
    filter_enum_type: type[FilterEnum],
    available_values: list[FilterEnum],
) -> ReplyKeyboardMarkup:
    return get_reply_keyboard(
        [
            KeyboardButton(
                translate(
                    get_button_string_id_from_filter_enum(
                        cast(FilterEnum, property),
                    )
                )
            )
            for property in filter_enum_type
            if property in available_values
        ],
    )


def verify_filter_reply_keyboard_choice(
    translate: Callable, filter_enum_type: type[FilterEnum], choice: str
) -> FilterEnum | None:
    for property in filter_enum_type:
        property = cast(FilterEnum, property)

        if choice == translate(
            get_button_string_id_from_filter_enum(property),
        ):
            return property

    return None


class AgeGroup(Enum):
    UNDER_20 = 20
    UNDER_30 = 30
    UNDER_40 = 40
    ABOVE_40 = 41


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
        await update.effective_message.reply_text(
            translate("environment_equipment_recommendation"),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=translate("equipment_shop_url_button"),
                            url=translate("equipment_shop_url"),
                        )
                    ],
                ]
            ),
        )

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
