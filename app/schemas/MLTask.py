from pydantic import BaseModel, ConfigDict
from typing import Dict, Any


class MLTaskCreate(BaseModel):
    local_model_id: int
    input_data: Dict[str, Any]


class MLTaskRead(BaseModel):
    ml_task_id: int
    user_id: int
    local_model_id: int
    input_data: Dict[str, Any]


class MLResultCreate(BaseModel):
    ml_task_id: int
    predict: int

    model_config = ConfigDict(protected_namespaces=())


class MLResultRead(BaseModel):
    ml_task_result_id: int
    ml_task_id: int
    predict: int

    model_config = ConfigDict(protected_namespaces=())


class PredictionInput(BaseModel):
    country: str
    currency: str
    prelaunch_activated: bool
    staff_pick: bool
    static_usd_rate: float
    fx_rate: float
    created_at: str
    launched_at: str
    deadline: str
    name: str
    blurb: str
    usd_goal: float
    name_city: str
    region: str
    type: str
    ppohasaction: str
    analytics_name: str
    position: int
    parent_name: str
    is_not_first_project: bool
    has_video: bool
    model_config = ConfigDict(protected_namespaces=())
