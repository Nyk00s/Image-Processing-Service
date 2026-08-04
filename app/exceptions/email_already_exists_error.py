from .base import DomainError

class EmailAlreadyExistsError(DomainError):
    status_code: int = 409
    detail: str = "Email already registered"
