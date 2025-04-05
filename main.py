import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sys
from pathlib import Path

# Фикс для PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    sys.path.append(str(BASE_DIR))

# Импорты после фикса путей
from routers.chat import router as change_chat
from utils.middlewares import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
    LogRequestsMiddleware,
)

app = FastAPI(title="Chat editor")

# Подключение компонентов
app.add_middleware(LogRequestsMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.include_router(change_chat)

if __name__ == "__main__":
    # Явное указание объекта приложения
    uvicorn.run(
        app,  # Используем сам объект app вместо строки
        host="0.0.0.0",
        port=8000,
        reload=False,
        loop="asyncio",  # Явно указываем цикл событий
        workers=1
    )