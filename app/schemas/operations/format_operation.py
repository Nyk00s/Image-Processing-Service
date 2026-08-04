from typing import Literal
from pydantic import BaseModel


class FormatOperation(BaseModel):
    type: Literal["format"]
    target: Literal["jpeg", "png", "webp"]
