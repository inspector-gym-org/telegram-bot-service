# mypy: disable-error-code="arg-type,index,union-attr"

from enum import Enum
from typing import Callable, cast

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..admin import notify_individual_plan
from ..payment import Item, ItemType, Payment, create_payment
from ..training_plan import (
    Environment,
    FilterEnum,
    Frequency,
    Goal,
    Level,
    Sex,
    get_property_values,
    get_training_plans,
)
from .constants import MenuState
from .equipment_shop import get_equipment_shop_keyboard
from .helpers import (
    get_reply_keyboard,
    get_translations,
    log_update_data,
    send_typing_action,
)
from .main_menu import get_main_menu, send_main_menu


class AgeGroup(Enum):
    UNDER_20 = 20
    UNDER_30 = 30
    UNDER_40 = 40
    ABOVE_40 = 41


def get_button_string_id_from_filter_enum(filter_enum: FilterEnum) -> str:
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
                    get_button_string_id_from_filter_enum(cast(FilterEnum, property))
                )
            )
            for property in filter_enum_type
            if property in available_values
        ],
        additional_row=[KeyboardButton(translate("previous_question"))],
    )


def verify_filter_reply_keyboard_choice(
    translate: Callable, filter_enum_type: type[FilterEnum], choice: str
) -> FilterEnum | None:
    for property in filter_enum_type:
        property = cast(FilterEnum, property)

        if choice == translate(get_button_string_id_from_filter_enum(property)):
            return property

    return None


@log_update_data
async def start_training_plan_survey(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("individual_training_plan_description"),
        reply_markup=get_reply_keyboard([KeyboardButton(translate("start_button"))]),
    )

    context.user_data["filters"] = {}
    return MenuState.INDIVIDUAL_PLAN_START


@log_update_data
@send_typing_action
@get_translations
async def ask_sex(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["filters"]["sex"] = None

    available_values = await get_property_values(Sex, context.user_data["filters"])

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
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await send_main_menu(update=update, context=context)

    if result := verify_filter_reply_keyboard_choice(translate, Sex, choice):
        context.user_data["filters"]["sex"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.SEX

    return await ask_age_group(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def ask_age_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["age_group"] = None

    await update.effective_message.reply_text(
        translate("age_group_description"),
        reply_markup=get_reply_keyboard(
            [
                KeyboardButton(translate("age_group_under_20_button")),
                KeyboardButton(translate("age_group_under_30_button")),
                KeyboardButton(translate("age_group_under_40_button")),
                KeyboardButton(translate("age_group_above_40_button")),
            ],
            additional_row=[KeyboardButton(translate("previous_question"))],
            keys_per_row=1,
        ),
    )

    return MenuState.AGE_GROUP


@log_update_data
@get_translations
async def save_age_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_sex(update=update, context=context)

    if choice == translate("age_group_under_20_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_20

    elif choice == translate("age_group_under_30_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_30

    elif choice == translate("age_group_under_40_button"):
        context.user_data["age_group"] = AgeGroup.UNDER_40

    elif choice == translate("age_group_above_40_button"):
        context.user_data["age_group"] = AgeGroup.ABOVE_40

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.AGE_GROUP

    return await ask_health_condition(
        update=update, context=context, translate=translate
    )


@log_update_data
@send_typing_action
async def ask_health_condition(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    await update.effective_message.reply_text(
        translate("health_condition_description"),
        reply_markup=get_reply_keyboard(
            [
                KeyboardButton(translate("health_condition_positive")),
                KeyboardButton(translate("health_condition_negative")),
            ],
            additional_row=[KeyboardButton(translate("previous_question"))],
        ),
    )

    return MenuState.HEALTH_CONDITION


@log_update_data
@get_translations
async def handle_health_condition(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_age_group(update=update, context=context, translate=translate)

    if choice == translate("health_condition_positive"):
        await update.effective_message.reply_text(
            translate("health_condition_on_positive")
        )

    elif choice == translate("health_condition_negative"):
        await update.effective_message.reply_text(
            translate("health_condition_on_negative"),
            reply_markup=get_main_menu(translate),
        )
        return MenuState.MAIN_MENU

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.HEALTH_CONDITION

    return await ask_goal(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def ask_goal(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["filters"]["goal"] = None

    available_values = await get_property_values(Goal, context.user_data["filters"])

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
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_health_condition(
            update=update, context=context, translate=translate
        )

    if result := verify_filter_reply_keyboard_choice(translate, Goal, choice):
        context.user_data["filters"]["goal"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.GOAL

    return await ask_environment(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def ask_environment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["filters"]["environment"] = None

    available_values = await get_property_values(
        Environment, context.user_data["filters"]
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
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_goal(update=update, context=context, translate=translate)

    if result := verify_filter_reply_keyboard_choice(translate, Environment, choice):
        context.user_data["filters"]["environment"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.ENVIRONMENT

    if context.user_data["filters"]["environment"] == Environment.HOUSE_AND_STREET:
        await update.effective_message.reply_text(
            translate("environment_equipment_recommendation"),
            reply_markup=get_equipment_shop_keyboard(translate),
        )

    return await ask_level(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def ask_level(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["filters"]["level"] = None

    available_values = await get_property_values(Level, context.user_data["filters"])

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
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_environment(
            update=update, context=context, translate=translate
        )

    if result := verify_filter_reply_keyboard_choice(translate, Level, choice):
        context.user_data["filters"]["level"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.LEVEL

    return await ask_frequency(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def ask_frequency(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    context.user_data["filters"]["frequency"] = None

    available_values = await get_property_values(
        Frequency, context.user_data["filters"]
    )

    if len(available_values) == 1:
        context.user_data["filters"]["frequency"] = available_values[0]
        return await send_payment_data(
            update=update, context=context, translate=translate
        )

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
    choice = update.effective_message.text

    if choice == translate("previous_question"):
        return await ask_level(update=update, context=context, translate=translate)

    if result := verify_filter_reply_keyboard_choice(translate, Frequency, choice):
        context.user_data["filters"]["frequency"] = result

    else:
        await update.effective_message.reply_text(translate("invalid_input_text"))
        return MenuState.FREQUENCY

    return await send_payment_data(update=update, context=context, translate=translate)


@log_update_data
@send_typing_action
async def send_payment_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    training_plan = (await get_training_plans(context.user_data["filters"]))[0]

    payment = await create_payment(
        Payment(
            _id="",  # will be generated by the database
            user={"telegram_id": update.effective_user.id},
            items=[
                Item(
                    price=training_plan.price,
                    item_type=ItemType.TRAINING_PLAN,
                    training_plan_id=training_plan.notion_id,
                )
            ],
        )
    )

    context.user_data["payment"] = payment
    context.user_data["training_plan"] = training_plan

    await update.effective_message.reply_text(
        translate("payment_training_plan_description").format(
            price=training_plan.price
        ),
        reply_markup=get_reply_keyboard(
            [KeyboardButton(translate("previous_question"))]
        ),
    )

    await update.effective_message.reply_text(translate("payment_monobank_card_data"))

    return MenuState.PAYMENT_SCREENSHOT


@log_update_data
@send_typing_action
@get_translations
async def save_payment_screenshot(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Callable
) -> MenuState:
    text = update.effective_message.text

    if text == translate("previous_question"):
        return await ask_frequency(update=update, context=context, translate=translate)

    if not update.message.photo:
        await update.effective_message.reply_text(translate("payment_not_screenshot"))
        return MenuState.PAYMENT_SCREENSHOT

    await notify_individual_plan(
        update.effective_message,
        payment=context.user_data["payment"],
        training_plan=context.user_data["training_plan"],
    )

    await update.effective_message.reply_text(
        translate("payment_wait_confirmation"), reply_markup=get_main_menu(translate)
    )

    context.user_data.clear()
    return MenuState.MAIN_MENU
