from pydantic import BaseSettings


class Settings(BaseSettings):
    app_root_path: str

    telegram_bot_token: str
    telegram_webhook_token: str

    redis_host: str
    redis_port: int
    redis_db: int

    user_service_url: str
    user_service_timeout: int

    training_plan_url: str
    training_plan_timeout: int


settings = Settings()  # type: ignore[call-arg]
