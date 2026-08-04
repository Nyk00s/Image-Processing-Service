from pydantic import Field
from typing import Union, Annotated
from .flip_operation import FlipOperation
from .crop_operation import CropOperation
from .sepia_operation import SepiaOperation
from .resize_operation import ResizeOperation
from .rotate_operation import RotateOperation
from .format_operation import FormatOperation
from .grayscale_operation import GrayscaleOperation
from .watermark_operation import WatermarkOperation

type Operation = Annotated[
    Union[
        CropOperation, 
        ResizeOperation, 
        RotateOperation, 
        GrayscaleOperation,
        FlipOperation,
        SepiaOperation,
        FormatOperation,
        WatermarkOperation
    ],
    Field(discriminator="type")
]