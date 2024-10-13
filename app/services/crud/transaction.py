from typing import List
from models.transaction import TransactionORM
from sqlalchemy import desc


def create_transaction(new_transaction: TransactionORM, session) -> None:
    with session:
        session.add(new_transaction)
        session.commit()
        session.refresh(new_transaction)


def get_all_transactions(session) -> List[TransactionORM]:
    with session:
        return session.query(TransactionORM).all()


def get_transactions_by_user_id(user_id: int, limit: int, session) -> List[TransactionORM]:
    with session:
        return (
            session.query(TransactionORM)
            .filter(TransactionORM.user_id == user_id)
            .order_by(desc(TransactionORM.date))
            .limit(limit)
            .all()
        )
