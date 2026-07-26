from datetime import datetime
from app.models import TaskStatus
from typing import Dict, Any, Optional
from pydantic import BaseModel, UUID4, ConfigDict


class TaskRead(BaseModel):
    id: UUID4
    picture_id: UUID4
    operations: Dict[str, Any]
    status: TaskStatus
    error_message: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    result_storage_key: Optional[str]

    model_config = ConfigDict(from_attributes=True)
