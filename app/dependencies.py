import jwt
import uuid
from typing import Optional
from app.database import get_db
from app.models import UserModel
from sqlalchemy.orm import Session
from app.tokens import decode_token
from app.services import UserService
from fastapi import HTTPException, Depends
from app.repositories import UserRepository
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def _resolve_token(
        token: str, 
        expected_type: str, 
        user_repo: UserRepository
) -> UserModel:
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    if payload["type"] != expected_type:
        raise HTTPException(401, "Invalid token")
    user = user_repo.get_by_id(uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(401, "Invalid token")
    if user.token_version != payload["token_version"]:
        raise HTTPException(401, "Invalid token")
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserModel:
    return _resolve_token(token, "access", user_repo)


def resolve_refresh_token(
    token: str,
    user_repo: UserRepository
):
    return _resolve_token(token, "refresh", user_repo)
