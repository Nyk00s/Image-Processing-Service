from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import PictureModel
from typing import Sequence, Optional


class PictureRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(self, picture: PictureModel) -> PictureModel:
        self.db.add(picture)
        self.db.commit()
        self.db.refresh(picture)
        return picture

    def get_by_id(self, id: UUID) -> Optional[PictureModel]:
        stmt = select(PictureModel).where(PictureModel.id == id)
        return self.db.scalar(stmt)

    def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Optional[PictureModel]:
        stmt = select(PictureModel).where(
            PictureModel.id == id, 
            PictureModel.user_id == user_id,
            PictureModel.deleted_at.is_(None)
        )
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: UUID, limit: int, offset: int) -> Sequence[PictureModel]:
        stmt = select(PictureModel).where(
            PictureModel.deleted_at.is_(None),
            PictureModel.user_id == user_id
        ).limit(limit).offset(offset)
        return self.db.scalars(stmt).all()

    def count_by_user(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(PictureModel).where(
            PictureModel.user_id == user_id,
            PictureModel.deleted_at.is_(None)
        )
        return self.db.scalar(stmt)
