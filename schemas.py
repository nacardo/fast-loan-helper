from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    email: str


class Loan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    loan_name: str
    loan_amount: float
    interest_rate: float
    daily_interest: float
    monthly_interest: float
    user_id: User
