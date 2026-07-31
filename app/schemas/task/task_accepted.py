from uuid import UUID
from pydantic import BaseModel
from app.models import TaskStatus


class TaskAccepted(BaseModel):
    task_id: UUID
    status: TaskStatus
