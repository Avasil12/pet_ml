from typing import List

import joblib
from models.MLTask import MLResult, MLtaskORM


def create_ml_task(ml_task: MLtaskORM, session) -> MLtaskORM:
    with session:
        session.add(ml_task)
        session.commit()
        session.refresh(ml_task)
        return ml_task


def create_result(ml_result: MLResult, session) -> MLtaskORM:
    with session:
        session.add(ml_result)
        session.commit()
        session.refresh(ml_result)
        return ml_result


def load_model(path_to_model) -> None:
    return joblib.load(path_to_model)


def get_ml_task_by_id(ml_task_id: int, session) -> MLtaskORM:
    with session:
        return session.query(MLtaskORM).filter(MLtaskORM.ml_task_id == ml_task_id).first()
    
    
def get_result_by_task_id(ml_task_id: int, session):
    with session:
        return session.query(MLResult).filter(MLResult.ml_task_id == ml_task_id).first()
    

def get_all_results(session):
    with session:
        return session.query(MLResult).all()


def get_all_tasks(session):
    with session:
        return session.query(MLtaskORM).all()


def get_ml_tasks_by_user_id(user_id: int, session) -> List[MLtaskORM]:
    with session:
        return session.query(MLtaskORM).filter(MLtaskORM.user_id == user_id).all()
