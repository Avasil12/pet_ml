import json
import os
import time
import pika
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from services.crud.user import get_user_id_by_email
from routes.balance import spend_balance
from database.database import get_session
from models.MLTask import MLtaskORM
from schemas.MLTask import MLResultCreate
from services.crud import MLTask as MLTaskServices
from fastapi.templating import Jinja2Templates
from fastapi import Request
from catboost import CatBoostClassifier
from auth.authenticate import authenticate_cookie

task_router = APIRouter(tags=['task'], prefix='/task')
result_router = APIRouter(tags=['result'], prefix='/result')
templates = Jinja2Templates(directory="view")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@task_router.get("/predict", response_class=HTMLResponse)
async def get_predict(request: Request, user: str = Depends(authenticate_cookie)):
    response = templates.TemplateResponse("predict.html", {"user": user, "request": request})
    return response


@task_router.post("/predict",  response_model=MLResultCreate, response_class=HTMLResponse)
async def post_predict(
    request: Request,
    user: str = Depends(authenticate_cookie),
    db: Session = Depends(get_session),
    country: str = Form(...),
    currency: str = Form(...),
    prelaunch_activated: bool = Form(...),
    staff_pick: bool = Form(...),
    static_usd_rate: float = Form(...),
    fx_rate: float = Form(...),
    created_at: str = Form(...),
    launched_at: str = Form(...),
    deadline: str = Form(...),
    name: str = Form(...),
    blurb: str = Form(...),
    usd_goal: float = Form(...),
    name_city: str = Form(...),
    region: str = Form(...),
    type: str = Form(...),
    ppohasaction: str = Form(...),
    analytics_name: str = Form(...),
    position: int = Form(...),
    parent_name: str = Form(...),
    is_not_first_project: bool = Form(...),
    has_video: bool = Form(...)
):
    user_id = get_user_id_by_email(user, db)
    if user_id is None:
        raise HTTPException(status_code=403, detail="User not authenticated")
    user_id = int(user_id)
    input_data = {
        'country': country,
        'currency': currency,
        'prelaunch_activated': prelaunch_activated,
        'staff_pick': staff_pick,
        'static_usd_rate': static_usd_rate,
        'fx_rate': fx_rate,
        'created_at': created_at,
        'launched_at': launched_at,
        'deadline': deadline,
        'name': name,
        'blurb': blurb,
        'usd_goal': usd_goal,
        'name_city': name_city,
        'region': region,
        'type': type,
        'ppohasaction': ppohasaction,
        'analytics_name': analytics_name,
        'position': position,
        'parent_name': parent_name,
        'is_not_first_project': is_not_first_project,
        'has_video': has_video
    }
    prediction_cost = 10

    balance_update = spend_balance(user_id=user_id, amount=prediction_cost, db=db)    
    if balance_update is None:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    ml_task = MLtaskORM(
        user_id=user_id,
        model_id=1,
        input_data=input_data
    )
    MLTaskServices.create_ml_task(ml_task, db)
    message = {
        "user_id": user_id,
        "input_data": input_data,
        "ml_task_id" : ml_task.ml_task_id
    }
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials(
            username=os.getenv('RABBITMQ_USER'),
            password=os.getenv('RABBITMQ_PASS') 
        )
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='prediction_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='prediction_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  
        )
    )

    connection.close()
    time.sleep(3)
    return RedirectResponse(url=f"/task/predict_task/{ml_task.ml_task_id}", status_code=303)


@task_router.get("/predict_task/{ml_task_id}", response_model=MLResultCreate, response_class=HTMLResponse)
async def get_prediction_result(ml_task_id: int,  request: Request, db: Session = Depends(get_session)):
    result = MLTaskServices.get_result_by_task_id(ml_task_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Prediction result not found")
    
    return templates.TemplateResponse("result.html", {"request": request, "result": result})
