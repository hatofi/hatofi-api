from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.user.user_services import UserService
from app.auth.authorization_token import (
    get_current_user,
    revoke_token,
    reusable_oauth2,
)
from app.core.database import get_db
from app.models.userModel import User
from app.schemas.userSchema import UserAuthResponse, UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.register_user(db, user)


@router.post("/login", response_model=UserAuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return UserService.login_user(db, form_data.username, form_data.password)


@router.get("/verify", response_model=UserResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(reusable_oauth2)) -> None:
    revoke_token(token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
