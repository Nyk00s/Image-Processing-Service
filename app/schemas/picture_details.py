from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4


class PictureDetails(BaseModel):
    id: UUID4
    user_id: UUID4
    presigned_url: str
    name: str
    mime: str
    size: int
    width: int
    height: int
    created_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
