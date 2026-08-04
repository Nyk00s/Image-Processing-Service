from typing import Literal
from pydantic import BaseModel


class FlipOperation(BaseModel):
    type: Literal["flip"]
    direction: Literal["horizontal", "vertical"]
