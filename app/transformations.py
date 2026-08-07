import os
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.schemas import Operation
from app.schemas.operations import ResizeOperation, GrayscaleOperation, CropOperation, RotateOperation, \
      FlipOperation, SepiaOperation, WatermarkOperation

_FLIP_MAP = {
    "horizontal": Image.Transpose.FLIP_LEFT_RIGHT,
    "vertical": Image.Transpose.FLIP_TOP_BOTTOM
}
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "fonts", "dejavu-sans.ttf")
MARGIN = 10


def calculate_position(
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeFontType,
        img_size: tuple[int, int],
        op: WatermarkOperation
) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), op.text, font=font)
    # for readability
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    image_w = img_size[0]
    image_h = img_size[1]

    if op.position == "top-left":
        return MARGIN, MARGIN
    elif op.position == "bottom-left":
        return MARGIN, image_h - text_h - MARGIN
    elif op.position == "top-right":
        return image_w - text_w - MARGIN, MARGIN
    elif op.position == "bottom-right":
        return image_w - text_w - MARGIN, image_h - text_h - MARGIN
    else:
        return (image_w - text_w) // 2, (image_h - text_h) // 2


def apply_resize(img: Image.Image, op: ResizeOperation) -> Image.Image:
    return img.resize((op.width, op.height))


def apply_grayscale(img: Image.Image, op: GrayscaleOperation) -> Image.Image:
    return img.convert('L')


def apply_crop(img: Image.Image, op: CropOperation) -> Image.Image:
    return img.crop((op.x, op.y, op.x + op.width, op.y + op.height))


def apply_rotate(img: Image.Image, op: RotateOperation) -> Image.Image:
    return img.rotate(op.angle, expand=True)


def apply_flip(img: Image.Image, op: FlipOperation) -> Image.Image:
    return img.transpose(_FLIP_MAP[op.direction])


def apply_sepia(img: Image.Image, op: SepiaOperation) -> Image.Image:
    img = img.convert("RGB")
    img_array = np.array(img)
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = np.dot(img_array, sepia_matrix.T).clip(0, 255).astype(np.uint8)
    return Image.fromarray(sepia_img)


def apply_watermark(img: Image.Image, op: WatermarkOperation) -> Image.Image:
    R, G, B = op.color
    img = img.convert('RGBA')
    txt = Image.new('RGBA', img.size, (R, G, B, 0))
    draw = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, op.size)
    pos = calculate_position(draw, font, img.size, op)
    draw.text(pos, op.text, font=font, fill=(R, G, B, op.opacity))
    return Image.alpha_composite(img, txt)


DISPATCH = {
    "resize": apply_resize,
    "grayscale": apply_grayscale,
    "crop": apply_crop,
    "rotate": apply_rotate,
    "flip": apply_flip,
    "sepia": apply_sepia,
    "watermark": apply_watermark
}


def process_image(data: bytes, operations: list[Operation]) -> tuple[bytes, str]:
    img = Image.open(io.BytesIO(data))
    output_format = img.format
    for op in operations:
        if op.type == "format":
            output_format = op.target.upper()
        else:
            img = DISPATCH[op.type](img, op)
    if output_format in ("JPEG", "JPG") and img.mode != "RGB":
        img = img.convert("RGB")
    out = io.BytesIO()
    img.save(out, format=output_format)
    return out.getvalue(), output_format
