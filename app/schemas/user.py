from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "user"
    chat_id: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=())


class UserRead(BaseModel):
    user_id: Optional[int]
    email: str
    role: Optional[str] = "user"
    chat_id: Optional[str]

    model_config = ConfigDict(protected_namespaces=())
