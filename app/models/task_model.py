import uuid
from .base import Base
from datetime import datetime
from .task_status import TaskStatus
from sqlalchemy import ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, mapped_column, Mapped


class TaskModel(Base):
    __tablename__ = 'tasks'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    picture_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('pictures.id'), nullable=False, index=True)
    operations: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False)
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    result_storage_key: Mapped[str | None] = mapped_column(nullable=True)

    picture = relationship('PictureModel', back_populates='tasks')
