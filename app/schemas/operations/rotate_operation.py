from typing import Literal
from pydantic import BaseModel

class RotateOperation(BaseModel):
    type: Literal["rotate"]
    angle: int
