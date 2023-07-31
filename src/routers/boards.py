from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.users import UserService
from services.boards import BoardService

from schemas import BoardBaseSchema, BoardCreateSchema, BoardSchema
from typing import List
from models import User

router = APIRouter(
    prefix="/boards",
    tags=["boards"],
)


@router.post("/create", response_model=BoardSchema)
async def create_board(
    board: BoardBaseSchema,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return await BoardService.create_board(db, board.name, board.is_public, token)


@router.put("/update", response_model=BoardSchema)
async def update_board(
    board_id: int,
    name: str,
    public: bool,
    token: str = Depends(UserService.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await BoardService.update_board(db, board_id, name, public, token)


@router.delete("/delete/{board_id}", response_model=dict)
async def delete_board(
    board_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await BoardService.delete_board(db, board_id, token)


@router.get("/get/{board_id}", response_model=BoardSchema)
async def get_board(
    board_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await BoardService.get_board_from_id(db, board_id, token)


# /list?page=1


@router.get("/list", response_model=List[BoardSchema])
async def get_all_accessible_boards(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return await BoardService.get_all_accessible_boards(db, token, page, size)
