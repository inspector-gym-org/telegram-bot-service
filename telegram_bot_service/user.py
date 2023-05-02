import httpx
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from .config import settings


class User(BaseModel):
    telegram_id: int

    first_name: str
    last_name: str | None
    username: str | None


async def create_user(user: User) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.user_service_url + "/",
            timeout=settings.user_service_timeout,
            json=jsonable_encoder(user),
        )

    return User(**response.json())
