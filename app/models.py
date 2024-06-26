from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    role: str | None = 'user'
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
