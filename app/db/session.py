# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from dotenv import load_dotenv
# import os

# load_dotenv()

# db_host = os.getenv("DB_HOSTNAME")
# db_port = os.getenv("DB_PORT")
# db_username = os.getenv("DB_USERNAME")
# db_password = os.getenv("DB_PASSWORD")

# SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/postgres"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()





from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

from app.core.config import get_settings
settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()