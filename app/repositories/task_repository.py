from uuid import UUID
from app.models import TaskModel, PictureModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Sequence


class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(self, task: TaskModel) -> TaskModel:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, id: UUID) -> Optional[TaskModel]:
        stmt = select(TaskModel).where(TaskModel.id == id)
        return self.db.scalar(stmt)

    def update(self, task: TaskModel) -> TaskModel:
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Optional[TaskModel]:
        stmt = (
            select(TaskModel)
            .join(PictureModel, TaskModel.picture_id == PictureModel.id)
            .where(PictureModel.user_id == user_id, TaskModel.id == id))
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: UUID) -> Sequence[TaskModel]:
        stmt = (
            select(TaskModel)
            .join(PictureModel, TaskModel.picture_id == PictureModel.id)
            .where(PictureModel.user_id == user_id)
        )
        return self.db.scalars(stmt).all()
