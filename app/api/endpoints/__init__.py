from enum import Enum
from pydantic import BaseModel


class Res(BaseModel):
    status: int
    message: str
    data: dict


class Scope(Enum):
    parts = "parts"
    accessories = "accessories"
