from datetime import datetime
from pydantic import BaseModel, UUID4, EmailStr, ConfigDict


class UserRead(BaseModel):
    id: UUID4
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
