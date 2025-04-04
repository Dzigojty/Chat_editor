from pydantic import BaseModel

class Chat(BaseModel):
    chat_id: int
    is_changeable: bool