from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TransactionORM(SQLModel, table=True):
    __tablename__ = "transactions"
    transaction_id: Optional[int] = Field(default=None, primary_key=True)
    cost: int
    user_id: int = Field(default=None, foreign_key="users.user_id")

    balance_old: int = Field(default=0)
    balance_now: int = Field(default=0)
    desc: str
    date: datetime = Field(default=datetime.now())

    class Config:
        protected_namespaces = ()
        from_attributes = True
