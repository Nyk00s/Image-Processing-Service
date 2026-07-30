from typing import Literal
from pydantic import BaseModel, Field

class CropOperation(BaseModel):
    type: Literal["crop"]
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)
