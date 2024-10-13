import joblib
from fastapi import APIRouter, Depends, HTTPException
from models.model import ModelORM
from typing import List
from sqlalchemy.orm import Session
from database.database import get_session
from schemas.model import ModelCreate, ModelRead
from services.crud import model as ModelServices

model_route = APIRouter(tags=['model'], prefix='/model')


@model_route.post("/", response_model=ModelCreate)
def create_model(model: ModelCreate, db: Session = Depends(get_session)) -> ModelCreate:
    db_model = ModelORM(**model.dict())
    db_model = ModelServices.create_model(db_model, db)
    return model


@model_route.get("/all", response_model=List[ModelRead])
def get_all_models(db: Session = Depends(get_session)) -> List[ModelRead]:
    models = ModelServices.get_all_models(db)
    if not models:
        raise HTTPException(status_code=404, detail="No models found")
    return models


@model_route.get("/{id}", response_model=ModelRead)
def get_model_by_id(id: int, db: Session = Depends(get_session)) -> ModelRead:
    model = ModelServices.get_model_by_id(id, db)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


def load_model(path_to_model: str):
    return joblib.load(f"/app/{path_to_model}")


