from .base import DomainError

class InvalidCredentialsError(DomainError):
    status_code: int = 401
    detail: str = "Invalid credentials"
