from typing import Any, Dict, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MLtaskORM(SQLModel, table=True):
    __tablename__ = "task"
    ml_task_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.user_id")
    model_id: int = Field(default=None, foreign_key="model.local_model_id")
    input_data: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))

    class Config:
        protected_namespaces = ()
        from_attributes = True


class MLResult(SQLModel, table=True):
    __tablename__ = "task_result"
    ml_task_result_id: Optional[int] = Field(default=None, primary_key=True)
    ml_task_id: int = Field(default=None, foreign_key="task.ml_task_id")
    predict: int

    class Config:
        protected_namespaces = ()
        from_attributes = True

