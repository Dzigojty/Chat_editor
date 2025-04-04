import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.middlewares import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
    LogRequestsMiddleware,
)

app = FastAPI(title="Chat editor")
# Подключение миддлвари и обработчиков ошибок для логов
app.add_middleware(LogRequestsMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
# Подключение рутов


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)