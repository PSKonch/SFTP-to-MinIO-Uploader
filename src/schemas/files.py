import uuid
from pydantic import BaseModel

from src.models.files import FileStatus

class FileSchemaCreate(BaseModel):
    server_id: uuid.UUID
    file_path: str
    file_name: str
    file_size: int
    checksum: str | None
    status: FileStatus
    minio_key: str | None
    error_message: str | None

class FileSchemaRead(BaseModel):
    id: uuid.UUID
    server_id: uuid.UUID
    file_path: str
    file_name: str
    file_size: int
    checksum: str | None
    status: FileStatus
    minio_key: str | None
    error_message: str | None

    class Config:
        from_attributes = True

class FileSchemaUpdate(BaseModel):
    server_id: uuid.UUID | None = None
    file_path: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    checksum: str | None = None
    status: FileStatus | None = None
    minio_key: str | None = None
    error_message: str | None = None

class FileSchemaDelete(BaseModel):
    id: uuid.UUID

class FileSchemaList(BaseModel):
    files: list[FileSchemaRead]
