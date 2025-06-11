import enum
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum as PgEnum, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.connection import Base

class FileStatus(enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    UPLOADED = "uploaded"
    NOTIFIED = "notified"
    ERROR = "error"

class FileModel(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column()
    file_name: Mapped[str] = mapped_column()
    file_size: Mapped[int] = mapped_column(BigInteger)
    checksum: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[FileStatus] = mapped_column(PgEnum(FileStatus), default=FileStatus.PENDING)
    minio_key: Mapped[str | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    server: Mapped["ServerModel"] = relationship(back_populates="files") # type: ignore
