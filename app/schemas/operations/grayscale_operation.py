from typing import Literal
from pydantic import BaseModel

class GrayscaleOperation(BaseModel):
    type: Literal["grayscale"]
