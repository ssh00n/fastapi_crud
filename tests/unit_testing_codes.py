import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordRequestForm

from ..models import User, Base
from ..schemas import UserCreate
from ..services.user_service import UserService
from ..database import SessionLocal

SQLALCHEMY_DATABASE_URL = "postgresql://test:testpassword@localhost:5433/test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_user(test_db):
    user_data = UserCreate(
        email="test@example.com",
        password="password1234",
        fullname="Test User",
    )
    user = UserService.create_user(test_db, user_data)
    assert user is not None
    assert user.email == user_data.email


def test_authenticate_user(test_db):
    user_data = UserCreate(
        email="test@example.com",
        password="password1234",
        fullname="Test User",
    )
    user = UserService.create_user(test_db, user_data)

    authenticated_user = UserService.authenticate_user(
        test_db, user_data.email, user_data.password
    )
    assert authenticated_user is not None
    assert authenticated_user.email == user_data.email
