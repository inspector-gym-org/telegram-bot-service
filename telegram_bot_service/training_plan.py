from enum import Enum
from uuid import UUID

import requests
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from .config import settings


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


class TrainingPlan(BaseModel):
    id: UUID

    title: str
    price: float

    sex: Sex
    goal: Goal
    level: Level
    frequency: Frequency
    environment: Environment


def get_training_plans(
    sex: Sex | None = None,
    goal: Goal | None = None,
    level: Level | None = None,
    frequency: Frequency | None = None,
    environment: Environment | None = None,
) -> list[TrainingPlan]:
    response = requests.get(
        url=settings.training_plan_url + "/",
        timeout=settings.training_plan_timeout,
        params=jsonable_encoder(
            {
                "sex": sex,
                "goal": goal,
                "level": level,
                "frequency": frequency,
                "environment": environment,
            },
        ),
    )

    return [TrainingPlan(**plan) for plan in response.json()]


def get_existing_property_values(
    filter_enum: type[FilterEnum],
    sex: Sex | None = None,
    goal: Goal | None = None,
    level: Level | None = None,
    frequency: Frequency | None = None,
    environment: Environment | None = None,
) -> list[FilterEnum]:
    response = requests.get(
        url=settings.training_plan_url + "/existing-property-values/",
        timeout=settings.training_plan_timeout,
        params=jsonable_encoder(
            {
                "property": filter_enum.__name__.lower(),
                "sex": sex,
                "goal": goal,
                "level": level,
                "frequency": frequency,
                "environment": environment,
            }
        ),
    )

    return [filter_enum(value) for value in response.json()]
