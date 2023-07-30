from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    board: BoardCreateSchema,
    db: Session = Depends(get_db),
    token: str = Depends(UserService.oauth2_scheme),
):
    return BoardService.create_board(db, board.name, board.is_public, token)


@router.put("/update", response_model=BoardSchema)
async def update_board(
    board_id: int,
    name: str,
    public: bool,
    token: str = Depends(UserService.oauth2_scheme),
    db: Session = Depends(get_db),
):
    return BoardService.update_board(db, board_id, name, public, token)


@router.delete("/delete/{board_id}", response_model=dict)
async def delete_board(
    board_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: Session = Depends(get_db),
):
    return BoardService.delete_board(db, board_id, token)


@router.get("/list", response_model=List[BoardSchema])
def get_all_accessible_boards(
    db: Session = Depends(get_db), token: str = Depends(UserService.oauth2_scheme)
):
    return BoardService.get_all_accessible_boards(db, token)


@router.get("/get/{board_id}", response_model=BoardSchema)
async def get_board(
    board_id: int,
    token: str = Depends(UserService.oauth2_scheme),
    db: Session = Depends(get_db),
):
    return BoardService.get_board_from_id(db, board_id, token)
