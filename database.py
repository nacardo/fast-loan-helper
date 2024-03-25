from sqlmodel import SQLModel, create_engine
from . import schemas

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
DATABASE_URL = "postgresql://admin:lh-pass2.@localhost/Loan"

engine = create_engine(
    DATABASE_URL
)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
