import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

SQLITE_PATH = os.getenv("SQLITE_PATH", "/data/avs.sqlite")

DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()