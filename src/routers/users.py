from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.users import UserService

# from fastapi.security import OAuth2PasswordRequestForm

from schemas import Token, TokenData, UserBase, UserCreate, UserLoginForm

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/signup", response_model=UserBase)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserService.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await UserService.create_user(db=db, user=user)


@router.post("/login", response_model=Token)
async def login_user(
    form_data: UserLoginForm,
    db: Session = Depends(get_db),
):
    return await UserService.login_user(db, form_data)
