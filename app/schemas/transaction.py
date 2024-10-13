from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    cost: int
    user_id: int
    balance_old: int
    balance_now: int
    desc: str
    date: Optional[datetime] = None

    model_config = ConfigDict(protected_namespaces=())


class TransactionRead(BaseModel):
    transaction_id: int
    cost: int
    user_id: int
    balance_old: int
    balance_now: int
    desc: str
    date: datetime

    model_config = ConfigDict(protected_namespaces=())
