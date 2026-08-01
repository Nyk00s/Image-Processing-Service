from PIL import Image
from app.schemas.operations import ResizeOperation, GrayscaleOperation



def apply_resize(img: Image.Image, op: ResizeOperation) -> Image.Image:
    return img.resize((op.width, op.height))


def apply_grayscale(img: Image.Image, op: GrayscaleOperation) -> Image.Image:
    return img.convert('L')


DISPATCH = {
    "resize": apply_resize,
    "grayscale": apply_grayscale
}
