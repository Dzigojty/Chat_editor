import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    SERVER_HOST: str
    SERVER_PORT: int

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    UPLOAD_DIR: str = "uploads"

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    EMOJI = "👀"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()