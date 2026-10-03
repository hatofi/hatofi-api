from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.auth.auth_services import UserService
from app.api.auth.auth_token import get_current_user
from app.core.database import get_db
from app.models.userModel import User
from app.schemas.userSchema import UserAuthResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.register_user(db, user)


@router.post("/login", response_model=UserAuthResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login a user with the provided credentials.
    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Session): The database session.
    Returns:
        UserAuthResponse: The response containing the access token and user information.
    """
    return UserService.login_user(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user