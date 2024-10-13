from fastapi import APIRouter, Depends, HTTPException
from typing import List
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_session
from schemas.transaction import TransactionCreate, TransactionRead
from services.crud import transaction as TransactionServices
from services.crud import user as UserServices

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

transactions_route = APIRouter(tags=['transactions'], prefix='/transactions')


@transactions_route.get("/all", response_model=List[TransactionRead])
def get_all_transactions(db: Session = Depends(get_session)) -> List[TransactionRead]:
    return TransactionServices.get_all_transactions(db)


@transactions_route.get("/", response_model=List[TransactionRead])
def get_transactions_by_user_id(limit = int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> List[TransactionRead]:
    current_user = UserServices.get_current_user(token, db)
    transactions = TransactionServices.get_transactions_by_user_id(current_user.user_id, limit, db)
    if not transactions:
        raise HTTPException(status_code=404, detail="Transactions not found")
    return transactions


@transactions_route.post("/", response_model=TransactionCreate)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_session)) -> TransactionCreate:
    TransactionServices.create_transaction(transaction, db)
    return transaction
