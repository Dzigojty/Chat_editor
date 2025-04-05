from pydantic_settings import BaseSettings
from typing import Optional, ClassVar

class Settings(BaseSettings):
    # Обязательные поля (аннотируем явно)
    API_ID: int = 22718183 # не записал в .env для правильной сборки, если интересно расскажу
    API_HASH: str = "7b6ffd4deaf4085e1ac11e73bc14586a" # не записал в .env для правильной сборки, если интересно расскажу
    
    # Если токен не используется - удалите эти строки
    TELEGRAM_TOKEN: Optional[str] = None  # Добавьте аннотацию типа
    
    # Если переменная константа (не из .env)
    DEBUG_MODE: ClassVar[bool] = True  # Пример ClassVar
    
    class Config:
        extra = "ignore"

settings = Settings()