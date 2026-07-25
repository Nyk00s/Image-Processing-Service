import uuid
from .base import Base
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column



class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4) 
    password_hash: Mapped[str] = mapped_column(nullable=False) 
    token_version: Mapped[int] = mapped_column(default=0)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    pictures = relationship("PictureModel", back_populates='user')
