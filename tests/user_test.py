from unittest.mock import patch, AsyncMock

from fastapi.security import OAuth2PasswordRequestForm
import pytest

# from ..database import SessionLocal, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# from ..models.models import define_models

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..schemas import UserCreate
from ..services.user_service import UserService
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://test:testpassword@localhost:25001/test"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User, Board, Post = define_models(Base)
# print(f"User : {User}, Board: {Board}, Post: {Post}")

Base.metadata.create_all(engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_user(db: Session):
    user_data = {
        "email": "test@example.com",
        "password": "password1234",
        "fullname": "Test User",
    }

    new_user = UserService.create_user(db, UserCreate(**user_data))

    assert new_user is not None
    assert new_user.email == user_data["email"]


def test_get_user(db: Session):
    user_data = {
        "email": "test@example.com",
        "password": "password1234",
        "fullname": "Test User",
    }

    UserService.create_user(db, UserCreate(**user_data))
    user = UserService.get_user(db, user_data["email"]).first()

    assert user is not None
    assert user.email == user_data["email"]


Base.metadata.drop_all(bind=engine)
