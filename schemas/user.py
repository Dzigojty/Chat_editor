from pydantic import BaseModel


class User(BaseModel):
    tg_id: str