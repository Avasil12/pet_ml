from typing import List

import joblib
from sqlalchemy import desc
from models.MLTask import MLResult, MLtaskORM
from models.user import User
from routes.model import get_model_by_id


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


def predict(ml_task_id, session):
    with session:
        ml_task = get_ml_task_by_id(ml_task_id, session)
        model = get_model_by_id(ml_task.id, session)
        loaded_model = load_model(model.path_to_model)
        features = ml_task.input_data
        prediction = loaded_model.predict([features])
        return prediction[0]


def get_ml_task_by_id(ml_task_id: int, session) -> MLtaskORM:
    with session:
        return session.query(MLtaskORM).filter(MLtaskORM.ml_task_id == ml_task_id).first()


def get_latest_result(chat_id: str, session):
    with session:
        user_task = session.query(User).filter(User.chat_id == chat_id).first()
        print(f"1s{user_task.chat_id}  work")
        if user_task:
            latest_task = session.query(MLtaskORM).filter(MLtaskORM.user_id == user_task.user_id).order_by(desc(MLtaskORM.ml_task_id)).first()
            print(f"2s{latest_task.ml_task_id} work")
        if latest_task:
            latest_result = session.query(MLResult).filter(MLResult.ml_task_id == latest_task.ml_task_id).first()
            print(f"3s{latest_result} WOOORK" )
            return latest_result
        else:
            return None


def get_all_results(session):
    with session:
        return session.query(MLResult).all()


def get_all_tasks(session):
    with session:
        return session.query(MLtaskORM).all()


def get_ml_tasks_by_user_id(user_id: int, session) -> List[MLtaskORM]:
    with session:
        return session.query(MLtaskORM).filter(MLtaskORM.user_id == user_id).all()
