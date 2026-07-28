from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import PictureModel, UserModel
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

    def list_by_user(self, user_id: UUID) -> Sequence[PictureModel]:
        stmt = select(PictureModel).where(PictureModel.user_id == user_id).where(PictureModel.deleted_at.is_(None))
        return self.db.scalars(stmt).all()
