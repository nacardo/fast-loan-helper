from sqlmodel import Field, SQLModel


class DBUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    email: str
    role: str | None


class DBLoan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    loan_name: str
    loan_amount: float
    interest_rate: float
    daily_interest: float
    monthly_interest: float
    user_id: int | None = Field(default=None, foreign_key="dbuser.id")

