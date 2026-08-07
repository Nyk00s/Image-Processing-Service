import os
import io
import pytest
from PIL import Image

TEST_IMAGE_NAME = 'test_image.jpg'


@pytest.fixture
def test_image():
    try:
        img = Image.open(os.path.join(os.path.dirname(__file__), 'assets', TEST_IMAGE_NAME))
        yield img
    finally:
        img.close()


@pytest.fixture
def make_image_bytes():
    def _make(size=(800, 600), fmt="PNG") -> bytes:
        buf = io.BytesIO()
        Image.new("RGB", size).save(buf, format=fmt)
        return buf.getvalue()
    return _make
