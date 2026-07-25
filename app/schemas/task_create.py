from typing import Dict, Any
from pydantic import BaseModel


class TaskCreate(BaseModel):
    operations: Dict[str, Any]
