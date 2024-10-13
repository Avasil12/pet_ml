from pydantic import BaseModel
from typing import Optional


class ModelCreate(BaseModel):
    name: str
    desc: str
    cost: int
    path: str


class ModelRead(BaseModel):
    model_id: Optional[int]
    name: str
    desc: str
    cost: int
    path: str

    class Config:
        protected_namespaces = ()