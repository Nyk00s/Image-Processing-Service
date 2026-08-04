from typing import Literal
from pydantic import BaseModel


class SepiaOperation(BaseModel):
    type: Literal["sepia"]
