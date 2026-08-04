from .base import DomainError

class InvalidImageError(DomainError):
    status_code: int = 400
    detail: str = "Invalid image"
