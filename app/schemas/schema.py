
from pydantic import BaseModel


class PredictRequest(BaseModel):
    ml_task_id: int
    predict: int

