from typing import Optional
from sqlmodel import SQLModel, Field


class BalanceORM(SQLModel, table=True):
    __tablename__ = "balance"
    balance_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.user_id")
    amount: int = Field(default=10)

    class Config:
        protected_namespaces = ()
        from_attributes = True
