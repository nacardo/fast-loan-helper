from sqlmodel import Session, select
from .database import create_db_and_tables, engine
from .schema import DBUser, DBLoan


def get_user(username: str) -> DBUser | None:
    """
    Return a user with the given username if the user exists
    :param username:
    :return:
    """
    with Session(engine) as session:
        statement = select(DBUser).where(DBUser.username == username)
        result = session.exec(statement).first()
        return DBUser.model_validate(result)


def get_users():
    with Session(engine) as session:
        statement = select(DBUser)
        results = session.exec(statement).all()
        # return results
        return [DBUser.model_validate(user) for user in results]


def create_users():
    paige = DBUser(username="paige", email="poo@gmail.com", password="paige_plain")
    sawyer = DBUser(username="sawyer", email="pup@gmail.com", password="pup123")

    with Session(engine) as session:
        session.add(paige)
        session.add(sawyer)

        session.commit()
        session.refresh(paige)
        session.refresh(sawyer)


def create_loans():
    paige_loan_1 = DBLoan(loan_name="sub 1",
                          loan_amount=29500.23,
                          interest_rate=5.04,
                          daily_interest=3.93,
                          monthly_interest=120.45,
                          user_id=1)
    paige_loan_2 = DBLoan(loan_name="sub 2",
                          loan_amount=3400.31,
                          interest_rate=5.04,
                          daily_interest=3.93,
                          monthly_interest=120.45,
                          user_id=1)
    with Session(engine) as session:
        session.add(paige_loan_1)
        session.add(paige_loan_2)
        session.commit()


def get_user_loans(user_id: int):
    with Session(engine) as session:

        statement = select(DBLoan.loan_name, DBLoan.loan_amount, DBLoan.monthly_interest).where(DBLoan.user_id == user_id)
        loans = session.exec(statement).all()
        print(loans)


def main():
    create_db_and_tables()
    create_users()
    create_loans()
    # print(get_user('paige').password)
    print(get_users())


if __name__ == '__main__':
    main()
