from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from models import Post
import datetime


# User Schema
class UserBaseSchema(BaseModel):
    fullname: str = Field(..., min_length=4, max_length=30)
    email: EmailStr = Field(..., max_length=50)


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=4, max_length=30)


class UserSchema(UserBaseSchema):
    id: int
    is_logged_in: bool

    class Config:
        orm_mode = True
        the_schema = {
            "user_demo": {"name": "demo", "email": "demo@demo.com", "password": "demo"}
        }

    """
    orm_mode -> True ?
    SQLAlchemy ORM의 객체와 호환성을 갖도록 함
    SQLAlchemy model instance는 ORM과 상호작용할 떄 기본적으로 lazy loading 방식을 사용하지만,
    Pydantic 모델은 지원하지 않기 때문에 orm_mode=True 를 설정해줌으로써 Pydantic 모델이 이러한 특성을 처리할 수 있도록 함
    """


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        the_schema = {"user_demo": {"email": "demo@demo.com", "password": "demo"}}


class UserInDBSchema(UserSchema):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str

    # Post Schema


class PostBaseSchema(BaseModel):
    title: str
    content: str


class PostCreateSchema(PostBaseSchema):
    pass


class PostSchema(PostBaseSchema):
    is_deleted: Optional[bool] = False
    post_id: int
    author_id: int
    board_id: int
    created_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


# Board Schema
class BoardBaseSchema(BaseModel):
    name: str
    is_public: bool = True


class BoardCreateSchema(BoardBaseSchema):
    pass


class BoardSchema(BoardBaseSchema):
    is_deleted: Optional[bool] = False
    board_id: int
    creator_id: int
    posts: Optional[List[PostSchema]] = []

    class Config:
        orm_mode = True
