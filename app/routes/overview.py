from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth.authenticate import authenticate_cookie
from database.database import get_session
from services.crud.user import get_user_id_by_email
from services.crud import transaction as TransactionServices
from services.crud import MLTask as MLServices
templates = Jinja2Templates(directory="view")

overview_route = APIRouter(tags=['overview'], prefix="/overview")


@overview_route.get("/user_overview")
async def user_overview(
    request: Request, 
    user: str = Depends(authenticate_cookie),
    db: Session = Depends(get_session),
    transaction_limit: int = 0,
    task_limit: int = 0
    ):
    user_id = get_user_id_by_email(user, db)

    transactions = TransactionServices.get_transactions_by_user_id(user_id, transaction_limit, db)
    ml_tasks_results = MLServices.get_ml_tasks_with_results(user_id, task_limit, db)

    return templates.TemplateResponse("user_overview.html", {
        "request": request,
        "transactions": transactions,
        "ml_tasks_results":  ml_tasks_results
    })
