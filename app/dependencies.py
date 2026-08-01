import jwt
import uuid
from app.config import Config
from functools import lru_cache
from app.database import get_db
from app.models import UserModel
from sqlalchemy.orm import Session
from app.tokens import decode_token
from app.storage import get_storage_client
from fastapi import HTTPException, Depends
from botocore.exceptions import ClientError
from fastapi.security import OAuth2PasswordBearer
from app.services import UserService, PictureService, TaskService
from app.repositories import UserRepository, PictureRepository, TaskRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@lru_cache
def get_settings() -> Config:
    return Config()


def get_task_repository(db: Session = Depends(get_db)):
    return TaskRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)


def get_picture_repository(db: Session = Depends(get_db)) -> PictureRepository:
    return PictureRepository(db)


def get_task_service(
        task_repo: TaskRepository = Depends(get_task_repository), 
        picture_repo: PictureRepository = Depends(get_picture_repository)
) -> TaskService:
    return TaskService(task_repo, picture_repo)


def ensure_bucket(s3_client, bucket: str) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket)


def get_picture_service(
        picture_repo: PictureRepository = Depends(get_picture_repository),
        settings: Config = Depends(get_settings)
) -> PictureService:
    return PictureService(get_storage_client(settings), picture_repo, settings.max_upload_size_mb)


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
) -> UserModel:
    return _resolve_token(token, "refresh", user_repo)
