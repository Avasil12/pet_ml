from typing import List

from fastapi.security import OAuth2PasswordBearer
from database.database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.balance import BalanceRead, BalanceUpdate
from services.crud import balance as BalanceServices
from services.crud import user as UserServices

balance_route = APIRouter(tags=['balance'], prefix="/balance")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@balance_route.get("/check")
async def check_balance(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> dict:
    current_user = UserServices.get_current_user(token, db)
    balance = BalanceServices.get_balance_by_id(current_user.user_id, db)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="balance not found")
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    return {"balance": balance.amount}


@balance_route.get("/all", response_model=List[BalanceRead])
def get_all_balances(db: Session = Depends(get_session)) -> List[BalanceRead]:
    return BalanceServices.get_all_balances(db)


@balance_route.post("/top_up", response_model=BalanceUpdate)
def top_up_balance(balance_update: BalanceUpdate, token: str = Depends(get_session), db: Session = Depends(get_session)) -> BalanceUpdate:
    current_user = UserServices.get_current_user(token, db)

    balance = BalanceServices.top_up_balance(current_user.user_id, balance_update.amount, db)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    return BalanceUpdate(amount=balance.amount)


@balance_route.post("/spend", response_model=BalanceUpdate)
def spend_balance(user_id: int, amount: int, db: Session = Depends(get_session)) -> BalanceUpdate:
    balance = BalanceServices.spend_balance(user_id, amount, db)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found funds")
    return balance
