from enum import Enum
from uuid import UUID

import httpx
from fastapi import status
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder

from .config import settings


class User(BaseModel):
    telegram_id: int


class ItemType(Enum):
    TRAINING_PLAN = 1


class Item(BaseModel):
    price: float

    item_type: ItemType
    training_plan_id: UUID | None


class PaymentStatus(Enum):
    ACCEPTED = 1
    REJECTED = 2

    PROCESSING = 3
    CREATED = 4


class Payment(BaseModel):
    id: str | None = Field(default=None, alias="_id")

    user: User
    items: list[Item]

    class Config:
        allow_population_by_field_name = True


async def create_payment(payment: Payment) -> Payment | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.payment_service_url + "/",
            timeout=settings.payment_service_timeout,
            json=jsonable_encoder(payment.dict(exclude={"id"})),
        )

    if response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        return None

    return Payment(**response.json())


async def update_payment(payment_id: str, new_status: PaymentStatus) -> Payment | None:
    async with httpx.AsyncClient() as client:
        response = await client.put(
            url=settings.payment_service_url + f"/{payment_id}/",
            timeout=settings.payment_service_timeout,
            json={"status": new_status.value},
        )

    if response.status_code != status.HTTP_200_OK:
        return None

    return Payment(**response.json())
