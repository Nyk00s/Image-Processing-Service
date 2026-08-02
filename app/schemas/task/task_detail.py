from typing import Optional
from datetime import datetime
from app.models import TaskStatus
from pydantic import BaseModel, UUID4, ConfigDict


class TaskDetail(BaseModel):
    id: UUID4
    picture_id: UUID4
    operations: list[dict]
    status: TaskStatus
    error_message: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
