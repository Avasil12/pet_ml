from pydantic import BaseModel
from typing import Optional


class ModelCreate(BaseModel):
    name: str
    de: str
    cost: int
    path_to_model: str


class ModelRead(BaseModel):
    model_id: Optional[int]
    name: str
    desc: str
    cost: int
    path_to_model: str

    class Config:
        protected_namespaces = ()