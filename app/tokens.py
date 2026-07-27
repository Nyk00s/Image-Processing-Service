import jwt
from uuid import UUID
from app.config import Config
from datetime import datetime, timezone, timedelta

settings = Config()


def create_access_token(user_id: UUID, token_version: int) -> str:
    return jwt.encode(
        payload={
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_ttl_minutes),
            "iat": datetime.now(timezone.utc),
            "type": "access",
            "token_version": token_version
        },
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(user_id: UUID, token_version: int) -> str:
    return jwt.encode(
        payload={
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days),
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "token_version": token_version
        },
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm] 
    )
