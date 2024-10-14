from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth.authenticate import authenticate_cookie
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
def get_transactions_by_user_id(limit: int = Query(default=2, ge=1), user: str = Depends(authenticate_cookie),  db: Session = Depends(get_session)) -> List[TransactionRead]:
    user_id = UserServices.get_user_id_by_email(user, db)
    transactions = TransactionServices.get_transactions_by_user_id(user_id, limit, db)
    if not transactions:
        raise HTTPException(status_code=404, detail="Transactions not found")
    return transactions


@transactions_route.post("/", response_model=TransactionCreate)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_session)) -> TransactionCreate:
    TransactionServices.create_transaction(transaction, db)
    return transaction
