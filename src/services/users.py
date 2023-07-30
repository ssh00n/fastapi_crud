from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from redis.exceptions import RedisError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from models import User

from utils.redis_manager import RedisManager
from schemas import UserBaseSchema


class UserService:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    redis = None
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return UserService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        return UserService.pwd_context.hash(password)

    @staticmethod
    def get_user_from_email(db: Session, email: str):
        try:
            return db.query(User).filter(User.email == email).first()
        except OperationalError:
            raise HTTPException(status_code=500, detail="Database connection error")

    @staticmethod
    def get_user_from_id(db: Session, user_id: int):
        try:
            return db.query(User).filter(User.id == user_id).first()
        except OperationalError:
            raise HTTPException(status_code=500, detail="Database connection error")

    @staticmethod
    def get_user_id_from_token(token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        print(f"requested_token: {token}")
        try:
            payload = jwt.decode(
                token,
                UserService.SECRET_KEY,
                algorithms=[UserService.ALGORITHM],
                # options={"verify_signature": False}, # for debugging
            )
            user_id = int(payload.get("sub"))
            print(f"user_id: {user_id}")
            return user_id

        except JWTError as e:
            print(f"JWTError: {e}")
            raise credentials_exception
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = UserService.get_user_from_email(db, email)
        if not user:
            return False
        if not UserService.verify_password(password, user.hash_password):
            return False
        return user

    @staticmethod
    async def create_access_token(*, data: dict, expires_delta: timedelta = 15):
        to_encode = data.copy()

        to_encode["sub"] = str(to_encode["sub"])

        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, UserService.SECRET_KEY, algorithm=UserService.ALGORITHM
        )

        try:
            redis = await RedisManager.get_connection()
            await redis.set(
                data["sub"],
                encoded_jwt,
                ex=expires_delta.seconds if expires_delta else 900,
            )
        except RedisError:
            raise HTTPException(status_code=500, detail="Failed to connect to Redis")

        return encoded_jwt

    @staticmethod
    def create_user(db: Session, user: UserBaseSchema):
        is_present = UserService.get_user_from_email(db, email=user.email)
        if is_present:
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = UserService.get_password_hash(user.password)
        db_user = User(
            email=user.email, fullname=user.fullname, hash_password=hashed_password
        )
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except:
            db.rollback()

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
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def get_current_user(db: Session, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, UserService.SECRET_KEY, algorithms=[UserService.ALGORITHM]
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception

            user = await UserService.get_user_from_id(db, user_id=user_id)
            if user is None:
                raise credentials_exception

            return user

        except JWTError:
            raise credentials_exception
        except Exception as e:
            print(e)
            raise credentials_exception

    @staticmethod
    async def logout_user(db: Session, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            redis = await RedisManager.get_connection()
            user = await UserService.get_current_user(db, token)
            if user:
                await redis.delete(user.id)
                return {"detail": "Successfully logged out"}

        except RedisError:
            raise HTTPException(status_code=500, detail="Failed to connect to Redis")
        except JWTError:
            raise credentials_exception
