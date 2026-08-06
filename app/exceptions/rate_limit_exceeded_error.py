from .base import DomainError


class RateLimitExceededError(DomainError):
    status_code: int = 429
    detail: str = "Upload rate limit exceeded"
