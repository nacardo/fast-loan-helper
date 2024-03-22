"""
Functions to work with multiple student loans and calculate monthly interests.
"""

from fastapi import FastAPI
import pandas as pd

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# FUNCTIONS
# todo calculate monthly interest

def calc_monthly_interest(dataframe: pd.DataFrame):
    """
    Given loan dataframe, use loan amount and interest rate to calculate daily interest rate,
     daily interest, and monthly interest
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


# todo determine payment order i.e. pay this much on load x then pay this much on loan y then ...


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
