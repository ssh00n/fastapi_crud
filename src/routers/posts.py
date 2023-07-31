from fastapi import APIRouter, Depends
from database import get_db
from schemas import PostBaseSchema, PostCreateSchema, PostSchema
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from services.users import UserService
from services.posts import PostService


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.post("/create", response_model=PostSchema)
async def create_post(
    board_id: int,
    title: str,
    content: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return await PostService.create_post(db, board_id, title, content, token)


@router.put("/update", response_model=PostSchema)
async def update_post(
    post_id: int,
    title: str,
    content: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return await PostService.update_post(db, post_id, title, content, token)


@router.delete("/delete/{board_id}", response_model=dict)
async def delete_post(
    post_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await PostService.delete_post(db, post_id, token)


@router.get("/get/{post_id}", response_model=PostSchema)
async def get_post_from_id(
    post_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await PostService.get_post_from_id(db, post_id, token)


@router.get("/list", response_model=List[PostSchema])
async def get_all_accessible_posts(
    board_id: int,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return await PostService.get_all_accessible_posts(db, board_id, token, page, size)
