import jwt
import uuid
from redis import Redis
from fastapi import Depends
from app.config import Config
from functools import lru_cache
from app.database import get_db
from app.models import UserModel
from app.cache import CacheClient
from sqlalchemy.orm import Session
from app.tokens import decode_token
from app.rate_limiter import RateLimiter
from app.storage import get_storage_client
from fastapi.security import OAuth2PasswordBearer
from app.services import UserService, PictureService, TaskService
from app.exceptions import RateLimitExceededError, InvalidTokenError
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
        picture_repo: PictureRepository = Depends(get_picture_repository),
        settings: Config = Depends(get_settings)
) -> TaskService:
    return TaskService(task_repo, picture_repo, get_storage_client(settings))


def get_picture_service(
        picture_repo: PictureRepository = Depends(get_picture_repository),
        settings: Config = Depends(get_settings)
) -> PictureService:
    return PictureService(
        get_storage_client(settings),
        get_storage_client(settings, public=True), 
        picture_repo, 
        settings.max_upload_size_mb
    )


def _resolve_token(
        token: str, 
        expected_type: str, 
        user_repo: UserRepository
) -> UserModel:
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
    if payload["type"] != expected_type:
        raise InvalidTokenError()
    user = user_repo.get_by_id(uuid.UUID(payload["sub"]))
    if user is None:
        raise InvalidTokenError()
    if user.token_version != payload["token_version"]:
        raise InvalidTokenError()
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


def get_cache_client(settings: Config = Depends(get_settings)) -> CacheClient:
    return CacheClient(Redis(settings.cache_host, settings.cache_port, decode_responses=True))


def get_rate_limiter(
    cache_client: CacheClient = Depends(get_cache_client),
    settings: Config = Depends(get_settings)
) -> RateLimiter:
    return RateLimiter(
        cache_client, 
        limit=settings.upload_rate_limit, 
        window_seconds=settings.rate_limit_window_seconds
    )


def check_upload_rate_limit(
    current_user: UserModel = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> None:
    key = f'ratelimit:upload:{current_user.id}'
    if not rate_limiter.check(key):
        raise RateLimitExceededError()
