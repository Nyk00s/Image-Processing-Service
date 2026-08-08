import uuid
import pytest
from datetime import datetime
from collections import namedtuple
from app.services import PictureService, UserService
from app.exceptions import PictureNotFoundError, InvalidCredentialsError
from .fakes import FakePictureRepository, FakeStorageClient, FakeUserRepository
from app.security import hash_password
from pydantic import SecretStr


def test_get_picture_returns_owner_picture(make_user, make_picture):

    owner_id = uuid.uuid4()
    user = make_user(
        id=owner_id, password_hash='sdfasdfasfas', token_version=20, 
        email='fake@gmail.com', created_at=datetime.now()
    )
    picture = make_picture(
        id=uuid.uuid4(), user_id=owner_id, storage_key="k", 
        name="x", mime="image/png", size=1, width=1, height=1, 
        deleted_at=None, created_at=datetime.now()
    )
    repo = FakePictureRepository([picture])
    service = PictureService(FakeStorageClient(), FakeStorageClient(), repo, max_upload_size_mb=10)

    result = service.get_picture(picture.id, user)
    assert result is not None
    assert result.url.startswith("https://fake-storage/")


def test_get_picture_raises_for_other_user(make_user, make_picture):
    picture = make_picture(
        id=uuid.uuid4(), user_id=uuid.uuid4(), storage_key="k", 
        name="x", mime="image/png", size=1, width=1, height=1, 
        deleted_at=None, created_at=datetime.now()
    )
    other_user = make_user(
            id=uuid.uuid4(), password_hash='sdfasdfasfas', token_version=20, 
            email='fake@gmail.com', created_at=datetime.now()
    )
    repo = FakePictureRepository([picture])
    service = PictureService(FakeStorageClient(), FakeStorageClient(), repo, max_upload_size_mb=10)

    with pytest.raises(PictureNotFoundError):
        service.get_picture(picture.id, other_user)


def test_list_pictures(make_picture, make_user):
    owner_id = uuid.uuid4()
    user = make_user(
        id=owner_id, password_hash='sdfasdfasfas', token_version=20, 
        email='fake@gmail.com', created_at=datetime.now()
    )
    pictures = [make_picture(
        id=uuid.uuid4(), user_id=owner_id, storage_key="k", 
        name="x", mime="image/png", size=i, width=i, height=i, 
        deleted_at=None, created_at=datetime.now()
    ) for i in range(5)]

    repo = FakePictureRepository(pictures)
    service = PictureService(FakeStorageClient(), FakeStorageClient(), repo, max_upload_size_mb=10)

    result = service.list_pictures(user, 1, 2)

    assert len(result.items) == 2
    assert result.page == 1
    assert result.per_page == 2
    assert result.total == 5


def test_authenticate_user(make_user, make_login):
    email = 'fake@gmail.com'
    password = 'random'

    login = make_login(email=email, password=SecretStr(password))
    user = make_user(
        id=uuid.uuid4(), password_hash=hash_password(password),
        token_version=0, email=email, created_at=datetime.now()
    )
    repo = FakeUserRepository([user])
    service = UserService(repo)


    result = service.authenticate(login)

    assert result is not None
    assert result.email == email


def test_authenticate_raises_invalid_credentials_wrong_email(make_user, make_login):
    email = 'fake@gmail.com'
    password = 'random'

    login = make_login(email='wrong_email', password=SecretStr(password))
    user = make_user(
        id=uuid.uuid4(), password_hash=hash_password(password),
        token_version=0, email=email, created_at=datetime.now()
    )
    repo = FakeUserRepository([user])
    service = UserService(repo)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(login)


def test_authenticate_raises_invalid_credentials_wrong_password(make_user, make_login):
    email = 'fake@gmail.com'
    password = 'random'

    login = make_login(email=email, password=SecretStr('wrong password'))
    user = make_user(
        id=uuid.uuid4(), password_hash=hash_password(password),
        token_version=0, email=email, created_at=datetime.now()
    )
    repo = FakeUserRepository([user])
    service = UserService(repo)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(login)
