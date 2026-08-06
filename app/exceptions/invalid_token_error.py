from .base import DomainError


class InvalidTokenError(DomainError):
    status_code: int = 401
    detail: str = 'Invalid token'
