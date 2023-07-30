from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services.users import UserService

from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from schemas import Token, UserBaseSchema, UserCreateSchema, UserLoginSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/signup", response_model=UserBaseSchema)
async def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    return UserService.create_user(db=db, user=user)


@router.post("/login", response_model=Token)
async def login_user(
    form_data: UserLoginSchema,
    db: Session = Depends(get_db),
):
    return await UserService.login_user(db, form_data)


@router.post("/logout")
async def logout_user(token: str, db: Session = Depends(get_db)):
    return await UserService.logout_user(db, token)


@router.post("/token")
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = UserService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=UserService.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await UserService.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    print(f"access_token: {access_token}")

    return {"access_token": access_token, "token_type": "bearer"}
