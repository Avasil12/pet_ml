from pydantic import BaseModel, ConfigDict
from typing import Optional


class BalanceUpdate(BaseModel):
    amount: int = 50

    class Config:
        orm_mode = True


class BalanceRead(BaseModel):
    balance_id: Optional[int]
    user_id: int
    amount: int
    
    model_config = ConfigDict(protected_namespaces=())
