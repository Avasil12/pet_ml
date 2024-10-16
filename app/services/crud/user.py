from models.balance import BalanceORM
from models.user import User
from typing import List, Optional


def get_all_users(session) -> List[User]:
    with session:
        return session.query(User).all()


def get_user_by_id(id: int, session) -> Optional[User]:
    users = session.get(User, id)
    if users:
        return users
    return None


def get_user_by_email(email: str, session) -> Optional[User]:
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user
    return None


def get_user_id_by_email(email: str, session) -> Optional[User]:
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user.user_id
    return None


def create_user(new_user: User, session) -> None:
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    balance = BalanceORM(user_id=new_user.user_id, amount=50)
    session.add(balance)
    session.commit()
    session.refresh(balance)
    return new_user
