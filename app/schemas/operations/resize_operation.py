from typing import Literal
from pydantic import BaseModel, Field

class ResizeOperation(BaseModel):
    type: Literal["resize"]
    width: int = Field(gt=0)
    height: int = Field(gt=0)
