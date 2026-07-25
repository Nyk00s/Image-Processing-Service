import uuid
from .base import Base
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column


class PictureModel(Base):
    __tablename__ = "pictures"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    mime: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    width: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user = relationship('UserModel', back_populates='pictures')
    tasks = relationship('TaskModel', back_populates='picture')
