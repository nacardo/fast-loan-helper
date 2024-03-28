import json
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from .database import create_db_and_tables, engine
from .models import UserInDB
from .security import get_password_hash
from .schema import DBUser, DBLoan
from .models import User, UserInDB


# USER
def get_user(username: str) -> DBUser | None:
    """
    Return a user with the given username if the user exists
    :param username:
    :return:
    """
    with Session(engine) as session:
        statement = select(DBUser).where(DBUser.username == username)
        result = session.exec(statement).first()
        if result:
            return DBUser.model_validate(result)


def get_users():
    with Session(engine) as session:
        statement = select(DBUser.username)
        results = session.exec(statement).all()
        return [DBUser.model_validate(user) for user in results]


def add_new_user(username: str, email: str, password: str) -> DBUser:
    if get_user(username):
        raise HTTPException(status_code=409, detail="User already exists")
    hashed_pass = get_password_hash(password)
    user = DBUser(username=username, email=email, password=hashed_pass)
    with Session(engine) as session:
        session.add(user)
        session.commit()
    return user


# def add_user(user: DBUser):
#     """
#     Add a user to the database.
#     :param user: User
#     :return:
#     """
#     user.password = get_password_hash(user.password)
#     print('USER TO ADD: ', user)
#     with Session(engine, expire_on_commit=False) as session:
#         session.add(user)
#         session.commit()


# LOAN
def get_loan(loan_id: int, user_id: int):
    """
    Get the loans for a specific user.
    :param loan_id:
    :param user_id:
    :return:
    """
    with Session(engine) as session:
        try:
            loan = session.exec(select(DBLoan).where(DBLoan.user_id == user_id, DBLoan.id == loan_id)).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not find that loan')
        return loan


def get_loans(user_id: int) -> List:
    """
    Get the loans for a specific user.
    :param user_id:
    :return:
    """
    with Session(engine) as session:
        loans = session.exec(select(DBLoan).where(DBLoan.user_id == user_id)).all()
        return [DBLoan.model_validate(loan) for loan in loans]


def add_loans(loans: DBLoan | List[DBLoan], user_id: int) -> None:
    """
    Add one or more loans to the database.
    :param user_id:
    :param loans:
    :return:
    """
    for loan in loans:
        loan.user_id = user_id
    loans_to_add = [loan for loan in loans if loan.id is None]
    loans_to_update = [loan for loan in loans if loan not in loans_to_add]

    # Update existing loans
    for loan in loans_to_update:
        print('updating loan', loan)
        update_loan(loan, user_id)

    # Add loans which don't have an id (new loans)
    with Session(engine) as session:
        if isinstance(loans, list):
            print('adding new loans', loans_to_add)
            session.add_all(loans_to_add)
            session.commit()

        if isinstance(loans, DBLoan):
            session.add(loans)
            session.commit()


def delete_loan(loan_id: int, user_id: int) -> None:
    with Session(engine) as session:
        statement = select(DBLoan).where(DBLoan.id == loan_id).where(DBLoan.user_id == user_id)
        try:
            loan = session.exec(statement).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not find loan to delete for user')
        session.delete(loan)
        session.commit()


def update_loan(loan: DBLoan, user_id: int, passed_session: Session | None = None):
    #
    # if passed_session:
    #     statement = select(DBLoan).where(DBLoan.id == loan.id).where(DBLoan.user_id == user_id)
    #     try:
    #         updated_loan = passed_session.exec(statement).one()
    #         updated_loan.loan_name = loan.loan_name
    #         updated_loan.loan_amount = loan.loan_amount
    #         updated_loan.interest_rate = loan.interest_rate
    #         updated_loan.daily_interest = loan.daily_interest
    #         updated_loan.monthly_interest = loan.monthly_interest
    #         passed_session.add(updated_loan)
    #         passed_session.commit()
    #         passed_session.refresh(updated_loan)
    #         return updated_loan
    #
    #     except NoResultFound:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not update loan for user')
    # else:
    with Session(engine) as session:
        statement = select(DBLoan).where(DBLoan.id == loan.id).where(DBLoan.user_id == user_id)
        try:
            updated_loan = session.exec(statement).one()
            updated_loan.loan_name = loan.loan_name
            updated_loan.loan_amount = loan.loan_amount
            updated_loan.interest_rate = loan.interest_rate
            updated_loan.daily_interest = loan.daily_interest
            updated_loan.monthly_interest = loan.monthly_interest
            session.add(updated_loan)
            session.commit()
            session.refresh(updated_loan)
            return updated_loan

        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Could not update loan: "{loan.loan_name}"')

