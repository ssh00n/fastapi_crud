from fastapi import APIRouter, Depends
from database import get_db
from schemas import PostBaseSchema, PostCreateSchema, PostSchema
from sqlalchemy.orm import Session

from services.users import UserService


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get("/get/{post_id}", response_model=PostSchema)
async def get_post_from_id(
    post_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: Session = Depends(get_db),
):
    return get_post_from_id(db, post_id, token)
