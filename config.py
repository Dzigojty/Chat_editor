from pydantic_settings import BaseSettings
from typing import Optional, ClassVar

class Settings(BaseSettings):
    # Обязательные поля (аннотируем явно)
    API_ID: int
    API_HASH: str
    
    # Если токен не используется - удалите эти строки
    TELEGRAM_TOKEN: Optional[str] = None  # Добавьте аннотацию типа
    
    # Если переменная константа (не из .env)
    DEBUG_MODE: ClassVar[bool] = True  # Пример ClassVar
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()