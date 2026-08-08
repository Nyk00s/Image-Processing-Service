import os
import io
import uuid
import pytest
from PIL import Image
from app.main import app
from datetime import datetime
from collections import namedtuple
from fastapi.testclient import TestClient
from app.dependencies import get_current_user

TEST_IMAGE_NAME = 'test_image.jpg'


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authed_client(make_user):
    user = make_user(password_hash='sdafasdf', token_version=3, email='a@b.com', created_at=datetime.now())
    app.dependency_overrides[get_current_user] = lambda: user
    client = TestClient(app)
    yield client, user
