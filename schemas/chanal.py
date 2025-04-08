from pydantic import BaseModel

class Chanal(BaseModel):
    user_id: str
    chanal_name: str
    chanal_id: str
    chanal_sub_num: int
    chanal_descr: str
