

class DomainError(Exception):
    status_code: int = 400
    detail: str = "Error"
