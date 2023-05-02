import httpx
from fastapi import status
from pydantic import BaseModel

from .config import settings


class User(BaseModel):
    telegram_id: int

    first_name: str
    last_name: str | None
    username: str | None


async def create_user(user: User) -> User | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.user_service_url + "/",
            timeout=settings.user_service_timeout,
            json=user.dict(),
        )

    if response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        return None

    return User(**response.json())
