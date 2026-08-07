import io
import math
import random
import pytest
from PIL import Image
from app.transformations import apply_resize, apply_grayscale, apply_watermark, apply_flip, apply_rotate,  \
    apply_crop, apply_sepia, process_image
from app.schemas.operations import ResizeOperation, GrayscaleOperation, WatermarkOperation, FlipOperation, \
    RotateOperation, CropOperation, SepiaOperation, FormatOperation


def test_resize_operation():
    test_img = Image.new(mode="RGB", size=(1920, 1080))
    op = ResizeOperation(type='resize', width=400, height=300)
    result = apply_resize(test_img, op)

    assert result.size == (400, 300)


def test_grayscale_operation():
    test_img = Image.new("RGB", size=(300, 300))
    op = GrayscaleOperation(type='grayscale')
    result = apply_grayscale(test_img, op)

    assert result.mode == 'L'


def test_crop_operation():
    test_img = Image.new("RGB", size=(1920, 1080))
    op = CropOperation(type='crop', x=0, y=0, width=400, height=300)
    result = apply_crop(test_img, op)

    assert result.size == (400, 300)


def test_crop_and_resize():
    test_image = Image.new("RGB", size=(1920, 1080))
    op_crop = CropOperation(type='crop', x=0, y=0, width=400, height=300)
    op_resize = ResizeOperation(type='resize', width=1000, height=500)

    result = apply_resize(test_image, op_resize)
    result = apply_crop(result, op_crop)

    assert result.size == (400, 300)


@pytest.mark.parametrize("angle", [10, 20, 30, 33, 40, 45, 60, 75, 80, 90, 180, 270, 360])
def test_rotate_operation(angle: int, test_image):
    w, h = test_image.size
    rad = math.radians(angle)
    wp = abs(w * math.cos(rad)) + abs(h * math.sin(rad))
    hp = abs(w * math.sin(rad)) + abs(h * math.cos(rad))

    op = RotateOperation(type='rotate', angle=angle)
    result = apply_rotate(test_image, op)
    wr, hr = result.size

    assert abs(wr - round(wp)) <= 2
    assert abs(hr - round(hp)) <= 2


def test_flip_horizontal_operation(test_image):
    op = FlipOperation(type='flip', direction='horizontal')
    result = apply_flip(test_image, op)
    assert test_image.getpixel((0, 0)) == result.getpixel((result.width - 1, 0))
    assert test_image.getpixel((0, test_image.height - 1)) == result.getpixel((result.width - 1, result.height - 1))
    assert test_image.getpixel((test_image.width - 1, 0)) == result.getpixel((0, 0))
    assert test_image.getpixel((test_image.width - 1, test_image.height - 1)) == result.getpixel((0, result.height - 1))


def test_flip_vertical_operation(test_image):
    op = FlipOperation(type='flip', direction='vertical')
    result = apply_flip(test_image, op)
    assert test_image.getpixel((0, 0)) == result.getpixel((0, result.height - 1))
    assert test_image.getpixel((test_image.width - 1, 0)) == result.getpixel((result.width - 1, result.height - 1))
    assert test_image.getpixel((0, test_image.height - 1)) == result.getpixel((0, 0))
    assert test_image.getpixel((test_image.width - 1, test_image.height - 1)) == result.getpixel((result.width - 1, 0))


def test_flip_vertical_and_horizontal_operation(test_image):
    op_hor = FlipOperation(type='flip', direction='horizontal')
    op_ver = FlipOperation(type='flip', direction='vertical')

    result = apply_flip(test_image, op_hor)
    result = apply_flip(result, op_ver)
    assert test_image.getpixel((0, 0)) == result.getpixel((result.width - 1, result.height - 1))
    assert test_image.getpixel((test_image.width - 1, 0)) == result.getpixel((0, result.height - 1))
    assert test_image.getpixel((0, test_image.height - 1)) == result.getpixel((result.width - 1, 0))
    assert test_image.getpixel((test_image.width - 1, test_image.height - 1)) == result.getpixel((0, 0))


def test_sepia_operation(test_image):
    op = SepiaOperation(type='sepia')
    result = apply_sepia(test_image, op)
    rand_x = random.randint(0, test_image.width - 1)
    rand_y = random.randint(0, test_image.height - 1)
    r, g, b = result.getpixel((rand_x, rand_y))

    assert r >= g >= b
    assert result.mode == "RGB"
    assert result.size == test_image.size


@pytest.mark.parametrize("position", ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'])
def test_watermark_operation(test_image, position):
    op = WatermarkOperation(type='watermark', text='sometext', position=position, size=60, opacity=255)
    result = apply_watermark(test_image, op)

    assert test_image.get_flattened_data() != result.get_flattened_data()
    assert test_image.size == result.size


def test_process_image_applies_chain(make_image_bytes):
    data = make_image_bytes()
    ops = [
        ResizeOperation(type="resize", width=400, height=300),
        GrayscaleOperation(type="grayscale"),
    ]
    result_bytes, _ = process_image(data, ops)

    result = Image.open(io.BytesIO(result_bytes))
    assert result.size == (400, 300)
    assert result.mode == "L"


@pytest.mark.parametrize('target', ['jpeg', 'png', 'webp'])
def test_format_operation(target, make_image_bytes):
    ops = [
        FormatOperation(type='format', target=target)
    ]
    _, fmt = process_image(make_image_bytes(), ops)
    assert fmt.lower() == target


def test_process_image_rejects_non_image():
    with pytest.raises(Exception):
        process_image(b'not an image', [])
