from pydantic import BaseModel, UUID4


class PictureCreate(BaseModel):
    user_id: UUID4
    storage_key: str
    name: str
    mime: str
    size: int
    width: int
    height: int
