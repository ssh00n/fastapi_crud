from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://developer:devpassword@localhost:25000/developer"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
session_create: Callable[[], Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def get_db() -> Session:
    db = session_create()
    try:
        yield db
    finally:
        db.close()
