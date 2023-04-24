from enum import Enum
from uuid import UUID

import requests
from fastapi import status
from pydantic import BaseModel, Field

from .config import settings


class User(BaseModel):
    telegram_id: int


class ItemType(Enum):
    TRAINING_PLAN = 1


class Item(BaseModel):
    price: float

    item_type: ItemType
    training_plan_id: UUID | None


class Payment(BaseModel):
    id: str | None = Field(default=None, alias="_id")

    user: User
    items: list[Item]

    class Config:
        allow_population_by_field_name = True


def create_payment(payment: Payment) -> Payment | None:
    response = requests.post(
        url=settings.payment_service_url + "/",
        timeout=settings.payment_service_timeout,
        data=payment.json(exclude={"id"}),
    )

    if response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        return None

    return Payment(**response.json())