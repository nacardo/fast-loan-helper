"""
Functions to work with multiple student loans and calculate monthly interests.
"""

import json
import os

import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv()

# created using:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

origins = ["http://localhost", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_users_db():
    with open('./database/db.json', 'r') as file:
        db = json.load(file)
        return db


def verify_password(plain_password, hashed_password):
    # compare password against existing hash
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    # return a hash of the plain password
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def add_new_user(db: dict, username: str, email: str, password: str):
    if get_user(db, username):
        raise HTTPException(status_code=409, detail="User already exists")
    hashed_pass = get_password_hash(password)
    user = UserInDB(username=username, email=email, hashed_password=hashed_pass, disabled=False)
    db.update({user.username: user})
    # Step 1: Read existing JSON data from file
    with open('./database/db.json', 'r') as file:
        existing_data = json.load(file)

    # Step 2: Add new entries to Python object
    new_entry = {user.username: user.model_dump()}
    existing_data.update(new_entry)

    # Step 3: Convert Python object back to JSON
    updated_data = json.dumps(existing_data, indent=4)

    # Step 4: Write updated JSON data back to file
    with open('./database/db.json', 'w') as file:
        file.write(updated_data)
    return user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    db = get_users_db()
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    print(form_data.__dict__)
    db = get_users_db()
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # create an access token with just the username.
    # the user has already been authenticate
    # above so there is no need to encode their password in the jwt.
    # only the username is needed.
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="Bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.post("/register", response_model=User)
async def register_user(
        # form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
        username: Annotated[str, Form()],
        email: Annotated[str, Form()],
        password: Annotated[str, Form()]
) -> UserInDB:
    db = get_users_db()
    user = add_new_user(db, username, email, password)
    # user = add_new_user(db, form_data.username, form_data.password)

    return user


# FUNCTIONS
# todo calculate monthly interest
def calc_monthly_interest(dataframe: pd.DataFrame):
    """
    Given loan dataframe, use loan amount and interest rate to calculate
     daily interest rate, daily interest, and monthly interest
    :param dataframe
    :return: dataframe
    """

    df = dataframe.copy()
    df['daily_interest_rate'] = df['interest_rate'] / 365

    # calc daily_interest
    df['daily_interest'] = df['loan_amount'] * df['daily_interest_rate']

    # calculate monthly_interest
    df['monthly_interest'] = df['loan_amount'] * df['daily_interest_rate'] * 30

    return df


# todo determine payment order
#  i.e. pay this much on load x then pay this much on loan y then ...


# ROUTES
## USER
# todo route that creates a user

# todo route that logs in a user

## LOANS
# todo route that gets the loans of a user

# todo route that receives the dataframe with all loans

# todo route that calculates one time payment

# todo route that adds a loan to the existing loans of user

# todo route that updates dataframe after payment is made
