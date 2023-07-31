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


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


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
