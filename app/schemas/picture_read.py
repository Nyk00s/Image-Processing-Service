from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4, ConfigDict


class PictureRead(BaseModel):
    id: UUID4
    user_id: UUID4
    storage_key: str
    name: str
    mime: str
    size: int
    width: int
    height: int
    created_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
