from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from enum import Enum as PyEnum


class UserRole(PyEnum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    __tablename__ = "users"
    user_id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
    role: str = Field(default="user")

    class Config:
        protected_namespaces = ()
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserSignIn(SQLModel):
    email: str
    password: str


class RegistrationForm(BaseModel):
    email: str
    password: str
