import uuid
from app.main import app
from datetime import datetime
from .fakes import FakePictureRepository, FakeStorageClient, FakeCacheClient
from app.services import PictureService
from app.dependencies import get_picture_service, get_cache_client


def test_login_missing_fields(client):
    result = client.post('/auth/login', json={"email": "a@b.com"})
    assert result.status_code == 422


def test_me_requires_auth(client):
    result = client.get("/auth/me")
    assert result.status_code == 401


def test_wrong_fields_values(authed_client):
    client, _ = authed_client
    result = client.get('/pictures?per_page=9999')
    assert result.status_code == 422


def test_get_picture_not_found_returns_404(authed_client):
    client, user = authed_client
    empty_repo = FakePictureRepository([])
    service = PictureService(FakeStorageClient(), FakeStorageClient(), empty_repo, max_upload_size_mb=10)
    app.dependency_overrides[get_picture_service] = lambda: service
    result = client.get(f"/pictures/{uuid.uuid4()}")
    assert result.status_code == 404


def test_get_picture_different_user_404(authed_client, make_user, make_picture):
    client, user = authed_client
    picture_id = uuid.uuid4()
    picture = make_picture(id=picture_id, user_id=uuid.uuid4(), storage_key="k", 
            name="x", mime="image/png", size=1, width=1, height=1, 
            deleted_at=None, created_at=datetime.now())
    repo = FakePictureRepository([picture])
    service = PictureService(FakeStorageClient(), FakeStorageClient(), repo, max_upload_size_mb=10)
    app.dependency_overrides[get_picture_service] = lambda: service
    result = client.get(f"/pictures/{picture_id}")
    assert result.status_code == 404


def test_rate_limit_429(authed_client, make_image_bytes):
    client, _ = authed_client
    service = PictureService(FakeStorageClient(), FakeStorageClient(), FakePictureRepository(), max_upload_size_mb=10)
    files = {"file": ("test.png", make_image_bytes(), "image/png")}

    app.dependency_overrides[get_cache_client] = lambda: FakeCacheClient()
    app.dependency_overrides[get_picture_service] = lambda: service
    result = client.post('/pictures', files=files)
    assert result.status_code == 429
