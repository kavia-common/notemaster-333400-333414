from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_session
from src.api.schemas import ErrorResponse, RegisterRequest, TokenResponse, UserMeResponse
from src.security.jwt import create_access_token
from src.services.users_service import UsersService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserMeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
    description="Register a new user account with email/password.",
    responses={
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    svc = UsersService(db)
    user = svc.register(email=payload.email, password=payload.password)
    return UserMeResponse(id=user.id, email=user.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate using email/password. Returns a JWT access token.\n\nNote: This endpoint expects OAuth2 form fields (username/password).",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    svc = UsersService(db)
    user = svc.authenticate(email=form_data.username, password=form_data.password)
    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Current user",
    description="Return the current authenticated user.",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
def me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = UsersService(db)
    user = svc.get_user_by_id(user_id)
    # get_current_user_id already validates existence, but keep it defensive.
    return UserMeResponse(id=user.id, email=user.email)
