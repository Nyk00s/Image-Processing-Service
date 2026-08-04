from .base import DomainError

class TaskNotFoundError(DomainError):
    status_code: int = 404
    detail: str = "Task not found"
