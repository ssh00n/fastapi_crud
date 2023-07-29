from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

from jose import jwt
import aioredis
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from models import User, Board, Post

from utils.redis_manager import RedisManager
from schemas import UserCreate


class UserService:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    redis = None
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return UserService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        return UserService.pwd_context.hash(password)

    @staticmethod
    def get_user(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = UserService.get_user(db, email)
        if not user:
            return False
        if not UserService.verify_password(password, user.hash_password):
            return False
        return user

    @staticmethod
    async def create_access_token(*, data: dict, expires_delta: timedelta = 15):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, UserService.SECRET_KEY, algorithm=UserService.ALGORITHM
        )

        redis = await RedisManager.get_connection()
        await redis.set(
            data["sub"], encoded_jwt, ex=expires_delta.seconds if expires_delta else 900
        )

        return encoded_jwt

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        hashed_password = UserService.get_password_hash(user.password)
        db_user = User(
            email=user.email, fullname=user.fullname, hash_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def login_user(db: Session, form_data: OAuth2PasswordRequestForm):
        user = UserService.authenticate_user(db, form_data.email, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(
            minutes=UserService.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = await UserService.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def logout_user(user_id: str):
        redis = await RedisManager.get_connection()
        await redis.delete(user_id)
        return {"detail": "Logged out"}
