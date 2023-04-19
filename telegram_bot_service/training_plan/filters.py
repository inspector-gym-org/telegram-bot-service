from enum import Enum
from typing import Callable, cast

from telegram import KeyboardButton, ReplyKeyboardMarkup


class Sex(Enum):
    __order__ = "MALE FEMALE"

    MALE = "Чоловік"
    FEMALE = "Жінка"


class Goal(Enum):
    __order__ = "MUSCLE_GAIN WEIGHT_LOSS IMPROVE_HEALTH"

    MUSCLE_GAIN = "Набір маси"
    WEIGHT_LOSS = "Схуднення"
    IMPROVE_HEALTH = "Рельєф"


class Level(Enum):
    __order__ = "BEGINNER MIDDLE ADVANCED"

    BEGINNER = "Початківець"
    MIDDLE = "Середній"
    ADVANCED = "Просунений"


class Frequency(Enum):
    __order__ = "TWICE THRICE FOUR"

    TWICE = "Двічі на тиждень"
    THRICE = "Тричі на тиждень"
    FOUR = "Чотири рази на тиждень"


class Environment(Enum):
    __order__ = "GYM HOUSE_AND_STREET"

    GYM = "Спортзал"
    HOUSE_AND_STREET = "Дім + вулиця"


FilterEnum = Sex | Goal | Environment | Level | Frequency


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
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    translate(
                        get_button_string_id_from_filter_enum(
                            cast(FilterEnum, property)
                        )
                    )
                )
            ]
            for property in filter_enum_type
            if property in available_values
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
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
