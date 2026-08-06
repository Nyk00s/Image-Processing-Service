import io
from PIL import Image
from uuid import uuid4, UUID
from fastapi import UploadFile
from app.storage import StorageClient
from app.repositories import PictureRepository
from app.models import UserModel, PictureModel
from app.schemas import PictureList, PictureDetail
from app.exceptions import MaxUploadSizeExceededError, InvalidImageError, PictureNotFoundError


class PictureService:

    def __init__(
            self, 
            storage: StorageClient, 
            public_storage: StorageClient,
            picture_repo: PictureRepository,
            max_upload_size_mb: int
        ):
        self.storage = storage
        self.public_storage = public_storage
        self.picture_repo = picture_repo
        self.max_upload_size_mb = max_upload_size_mb

    async def upload(self, upload: UploadFile, user: UserModel) -> PictureModel:
        if upload.size is None or upload.size > self.max_upload_size_mb * 1024 * 1024:
            raise MaxUploadSizeExceededError()
        data = await upload.read()
        try:
            with Image.open(io.BytesIO(data)) as img:
                img.verify()
            with Image.open(io.BytesIO(data)) as img:
                width, height = img.size
                fmt = img.format
                ext = fmt.lower()
                mime = Image.MIME.get(fmt)
        except Exception:
            raise InvalidImageError()
        if fmt not in {"JPEG", "PNG", "WEBP"}:
            raise InvalidImageError()
        storage_key = f"users/{user.id}/originals/{uuid4()}.{ext}"
        self.storage.upload(storage_key, data, mime)
        picture = PictureModel(
            user_id=user.id,
            storage_key=storage_key,
            name=upload.filename,
            mime=mime,
            size=len(data),
            width=width,
            height=height,
        )
        try:
            picture = self.picture_repo.add(picture)
        except Exception:
            self.storage.delete(storage_key)
            raise
        return picture

    def get_picture(self, id: UUID, user: UserModel) -> PictureDetail:
        if not (picture := self.picture_repo.get_by_id_and_user(id, user.id)):
            raise PictureNotFoundError()
        return PictureDetail(
            id=picture.id, name=picture.name, mime=picture.mime,
            size=picture.size, width=picture.width, height=picture.height,
            created_at=picture.created_at, url=self.public_storage.generate_presigned_url(picture.storage_key),
        )

    def list_pictures(self, user: UserModel, page: int, per_page: int) -> PictureList:
        pictures = self.picture_repo.list_by_user(user.id, per_page, (page - 1) * per_page)
        user_picture_count = self.picture_repo.count_by_user(user.id)
        return PictureList(
            items=pictures,
            total=user_picture_count,
            page=page,
            per_page=per_page
        )