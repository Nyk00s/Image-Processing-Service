from pydantic import BaseModel
from app.schemas.operations import Operation


class TaskCreate(BaseModel):
    operations: list[Operation]
