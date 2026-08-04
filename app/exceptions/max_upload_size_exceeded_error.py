from .base import DomainError

class MaxUploadSizeExceededError(DomainError):
    status_code: int = 413
    detail: str = "Image exceeds allowed size"
