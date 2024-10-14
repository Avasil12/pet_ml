from typing import List

from fastapi.security import OAuth2PasswordBearer
from auth.authenticate import authenticate_cookie
from database.database import get_session
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from schemas.balance import BalanceRead, BalanceUpdate
from services.crud import balance as BalanceServices
from services.crud import user as UserServices

balance_route = APIRouter(tags=['balance'], prefix="/balance")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@balance_route.get("/check")
async def check_balance(user: str = Depends(authenticate_cookie), db: Session = Depends(get_session)) -> dict:
    user_id = UserServices.get_user_id_by_email(user, db)
    balance = BalanceServices.get_balance_by_id(user_id, db)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="balance not found")

    return {"balance": balance.amount}


@balance_route.get("/all", response_model=List[BalanceRead])
def get_all_balances(db: Session = Depends(get_session)) -> List[BalanceRead]:
    return BalanceServices.get_all_balances(db)


@balance_route.post("/top_up", response_model=BalanceUpdate)
def top_up_balance(amount: int = Form(...), user: str = Depends(authenticate_cookie),  db: Session = Depends(get_session)) -> BalanceUpdate:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    user_id = UserServices.get_user_id_by_email(user, db)
    balance = BalanceServices.top_up_balance(user_id, amount, db)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    return BalanceUpdate(amount=balance.amount)


@balance_route.post("/spend", response_model=BalanceUpdate)
def spend_balance(user_id: int, amount: int, db: Session = Depends(get_session)) -> BalanceUpdate:
    balance = BalanceServices.spend_balance(user_id, amount, db)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found funds")
    return balance
