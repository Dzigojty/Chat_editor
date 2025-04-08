from pydantic_settings import BaseSettings
from typing import Optional, ClassVar
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Обязательные поля (аннотируем явно)
    API_ID: int
    API_HASH: str
    
    # Если токен не используется - удалите эти строки
    TELEGRAM_TOKEN: Optional[str] = None  # Добавьте аннотацию типа
    
    # Если переменная константа (не из .env)
    DEBUG_MODE: ClassVar[bool] = True  # Пример ClassVar
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()