from typing import List
from pydantic import BaseModel
from .picture_read import PictureRead


class PictureList(BaseModel):
    items: List[PictureRead]
    total: int
    page: int
    per_page: int
