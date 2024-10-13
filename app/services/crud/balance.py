from typing import List
from models.balance import BalanceORM
from models.transaction import TransactionORM


def get_all_balances(session) -> List[BalanceORM]:
    with session:
        return session.query(BalanceORM).all()


def get_balance_by_id(user_id: int, session) -> BalanceORM:
    with session:
        return session.query(BalanceORM).filter(BalanceORM.user_id == user_id).first()


def top_up_balance(user_id: int, amount: int, session):
    with session:
        balance = session.query(BalanceORM).filter(BalanceORM.user_id == user_id).first()
        if balance:
            balance_old = balance.amount
            balance.amount += amount
            transaction = TransactionORM(cost=amount, user_id=user_id,
                                         desc="top",
                                         balance_old=balance_old,
                                         balance_now=balance.amount)
            session.add(transaction)
            session.commit()
            session.refresh(balance)
            return balance
        return None


def spend_balance(user_id: int, amount: int, session):
    with session:
        balance = session.query(BalanceORM).filter(BalanceORM.user_id == user_id).first()
        if balance and balance.amount >= amount:
            balance.amount -= amount
            transaction = TransactionORM(cost=amount,
                                         user_id=user_id,
                                         desc="spend",
                                         balance_now=balance.amount)
            session.add(transaction)
            session.commit()
            session.refresh(balance)
            return balance
        return None
