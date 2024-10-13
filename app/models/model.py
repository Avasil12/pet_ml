from typing import Optional
from sqlmodel import SQLModel, Field


class ModelORM(SQLModel, table=True):
    __tablename__ = "model"
    model_id:  Optional[int] = Field(default=None, primary_key=True)
    name: str
    desc: str
    cost: int
    path: str

    class Config:
        protected_namespaces = ()
        from_attributes = True
