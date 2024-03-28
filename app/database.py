from sqlmodel import SQLModel, create_engine

# DATABASE_URL = "postgresql+psycopg2://admin:lh-pass2.@localhost/Loan"
sqlite_file_name = "/Users/nickcardoza/Dev/apis/interest-calc/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

