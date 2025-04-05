from pydantic import BaseModel

class User(BaseModel):
    api_id: int
    api_hash: str