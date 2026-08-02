from pydantic import BaseModel
from .task_read import TaskRead


class TaskList(BaseModel):
    tasks: list[TaskRead]
    page: int
    per_page: int
    total: int
