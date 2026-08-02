from pydantic import BaseModel
from .picture_read import PictureRead


class PictureList(BaseModel):
    items: list[PictureRead]
    total: int
    page: int
    per_page: int
