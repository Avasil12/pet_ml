
from database.database import get_session, init_db
from models.user import UserORM
from services.crud.balance import spend_balance, top_up_balance
from services.crud.transaction import get_all_transactions
from services.crud.user import create_user 


if __name__ == "__main__":
    init_db()
    test_user_1 = UserORM(email='avasil@mail.ru', password='test1')
    test_user_2 = UserORM(email='test@mail.ru', password='test2')
    session = get_session()
    create_user(test_user_1, session)
    create_user(test_user_2, session)
    
    user_id = 1
    amount = 100
    updated_balance = top_up_balance(user_id, amount, session)
    if updated_balance:
        print(f"новый баланс: {updated_balance.amount}")
    else:
        print("Провал")
    amount = 50
    updated_balance = spend_balance(user_id, amount, session)
    if updated_balance:
        print(f" новый баланс: {updated_balance.amount}")
    else:
        print("Провал")
    all_transactions = get_all_transactions(session)
    for transaction in all_transactions:
        print(f" {transaction.transaction_id} стоимость {transaction.cost}, 
              пользователь {transaction.user_id}, Desc {transaction.description}, дата {transaction.date}")    
    session.close()