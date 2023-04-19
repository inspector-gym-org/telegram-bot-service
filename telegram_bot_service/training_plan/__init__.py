from uuid import UUID

import requests
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ..config import settings
from .filters import Environment, FilterEnum, Frequency, Goal, Level, Sex


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
