import os
import io
import uuid
import pytest
from PIL import Image
from datetime import datetime
from collections import namedtuple

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


@pytest.fixture
def make_user():
    User = namedtuple('User', ['id', 'password_hash', 'token_version', 'email', 'created_at'])
    def _make(id=None, **kw):
        return User(id=id or uuid.uuid4(), **kw)
    return _make


@pytest.fixture
def make_picture():
    Picture = namedtuple('Picture', ['id', 'user_id', 'storage_key', 'name', 'mime', 'size', 'width', 'height', 'deleted_at', 'created_at'])
    def _make(user_id, id=None, **kw):
        return Picture(id=id or uuid.uuid4(), user_id=user_id, **kw)
    return _make


@pytest.fixture
def make_login():
    Login = namedtuple('Login', ['email', 'password'])
    def _make(**kw):
        return Login(**kw)
    return _make