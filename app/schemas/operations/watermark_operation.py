from typing import Literal, Annotated
from pydantic import BaseModel, Field

RgbChannel = Annotated[int, Field(ge=0, le=255)]
RgbColor = tuple[RgbChannel, RgbChannel, RgbChannel]


class WatermarkOperation(BaseModel):
    type: Literal["watermark"]
    text: str
    position: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    size: int = Field(gt=0)
    opacity: int = Field(ge=0, le=255)
    color: RgbColor = (255, 255, 255)
