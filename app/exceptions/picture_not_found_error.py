from .base import DomainError

class PictureNotFoundError(DomainError):
    status_code: int = 404
    detail: str = "Picture not found"
