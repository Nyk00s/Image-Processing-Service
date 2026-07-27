from uuid import UUID
from typing import Optional
from sqlalchemy import select
from app.models import UserModel
from sqlalchemy.orm import Session


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.email == email)
        return self.db.scalar(stmt)

    def add_user(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, id: UUID) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.id == id)
        return self.db.scalar(stmt)

    def increment_token_version(self, user: UserModel) -> None:
        user.token_version += 1
        self.db.commit()
