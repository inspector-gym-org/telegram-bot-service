from enum import Enum
from typing import TypedDict
from uuid import UUID

import httpx
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
    url: str

    title: str
    price: float
    content_url: str


class Filters(BaseModel):
    sex: Sex | None
    goal: Goal | None
    environment: Environment | None
    level: Level | None
    frequency: Frequency | None


class FiltersDict(TypedDict):
    sex: Sex | None
    goal: Goal | None
    environment: Environment | None
    level: Level | None
    frequency: Frequency | None


async def get_training_plans(
    filters: FiltersDict,
) -> list[TrainingPlan]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=settings.training_plan_service_url + "/",
            timeout=settings.training_plan_service_timeout,
            params=jsonable_encoder(
                Filters(**filters).dict(exclude_none=True),
            ),
        )

    return [TrainingPlan(**plan) for plan in response.json()]


async def get_training_plan(training_plan_id: UUID) -> TrainingPlan:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=settings.training_plan_service_url + f"/{training_plan_id.hex}/",
            timeout=settings.training_plan_service_timeout,
        )

    return TrainingPlan(**response.json())


async def get_property_values(
    filter_enum: type[FilterEnum],
    filters: FiltersDict,
) -> list[FilterEnum]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=settings.training_plan_service_url
            + f"/property/{filter_enum.__name__.lower()}/",
            timeout=settings.training_plan_service_timeout,
            params=jsonable_encoder(
                Filters(**filters).dict(exclude_none=True),
            ),
        )

    return [filter_enum(value) for value in response.json()]
