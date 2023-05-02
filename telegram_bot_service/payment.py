from enum import Enum

import httpx
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from .config import settings


class User(BaseModel):
    telegram_id: int


class ItemType(Enum):
    TRAINING_PLAN = 1


class Item(BaseModel):
    price: float

    item_type: ItemType
    training_plan_id: str | None


class PaymentStatus(Enum):
    ACCEPTED = 1
    REJECTED = 2

    PROCESSING = 3
    CREATED = 4


class Payment(BaseModel):
    id: str

    user: User
    items: list[Item]

    class Config:
        allow_population_by_field_name = True


async def create_payment(payment: Payment) -> Payment:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.payment_service_url + "/",
            timeout=settings.payment_service_timeout,
            json=jsonable_encoder(payment, exclude={"id"}),
        )

    return Payment(**response.json())


async def update_payment(payment_id: str, new_status: PaymentStatus) -> Payment:
    async with httpx.AsyncClient() as client:
        response = await client.put(
            url=settings.payment_service_url + f"/{payment_id}/",
            timeout=settings.payment_service_timeout,
            json={"status": new_status.value},
        )

    return Payment(**response.json())
