from pydantic import BaseModel, EmailStr
from typing import Optional


# User Schema
class UserBase(BaseModel):
    fullname: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_logged_in: bool

    class Config:
        orm_mode = True

    """
    orm_mode -> True ?
    SQLAlchemy ORM의 객체와 호환성을 갖도록 함
    SQLAlchemy model instance는 ORM과 상호작용할 떄 기본적으로 lazy loading 방식을 사용하지만,
    Pydantic 모델은 지원하지 않기 때문에 orm_mode=True 를 설정해줌으로써 Pydantic 모델이 이러한 특성을 처리할 수 있도록 함
    """


class UserLoginForm(BaseModel):
    email: EmailStr
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    fullname: str | None = None


# Board Schema
class BoardBase(BaseModel):
    name: str
    is_public: bool = True


class BoardCreate(BoardBase):
    pass


class Board(BoardBase):
    id: int
    creator_id: int

    class Config:
        orm_mode = True


# Post Schema
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    author_id: int
    board_id: int

    class Config:
        orm_mode = True
