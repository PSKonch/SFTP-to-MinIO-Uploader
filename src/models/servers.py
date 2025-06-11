import enum
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum as PgEnum, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.connection import Base

class ServerModel(Base):
    __tablename__ = "servers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host: Mapped[str] = mapped_column()
    port: Mapped[int] = mapped_column(default=22)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    folder_path: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    files: Mapped[list["FileModel"]] = relationship(back_populates="server", cascade="all, delete-orphan") # type: ignore
