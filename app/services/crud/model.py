from typing import List
from models.model import ModelORM


def get_model_by_id(id: int, session) -> ModelORM:
    with session:
        return session.query(ModelORM).filter(ModelORM.id == local_model_id).first()


def get_all_models(session) -> List[ModelORM]:
    with session:
        return session.query(ModelORM).all()


def create_model(new_model: ModelORM, session) -> None:
    with session:
        db_model = ModelORM.from_orm(new_model)
        session.add(db_model)
        session.commit()
        session.refresh(db_model)
