from pydantic import Field
from typing import Union, Annotated
from .crop_operation import CropOperation
from .resize_operation import ResizeOperation
from .rotate_operation import RotateOperation
from .grayscale_operation import GrayscaleOperation

type Operation = Annotated[
    Union[CropOperation, ResizeOperation, RotateOperation, GrayscaleOperation],
    Field(discriminator="type")
]