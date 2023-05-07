from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_webhook_token: str

    redis_host: str
    redis_port: int

    redis_language_db: int
    redis_admin_notification_db: int

    user_service_url: str
    user_service_timeout: int

    training_plan_service_url: str
    training_plan_service_timeout: int

    payment_service_url: str
    payment_service_timeout: int

    bot_admin_chat_ids: list[int]
    bot_developer_chat_ids: list[int]

    log_level: str
    log_format: str
    log_date_format: str


settings = Settings()  # pyright: ignore [reportGeneralTypeIssues]
