import uuid
from datetime import datetime
from pydantic import BaseModel

class ServerSchemaCreate(BaseModel):
    id: uuid.UUID | None = None
    host: str
    port: int | None = 22
    username: str
    password: str
    folder_path: str
    is_active: bool | None = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

class ServerSchemaRead(BaseModel):
    id: uuid.UUID
    host: str
    port: int | None = 22
    username: str
    password: str
    folder_path: str
    is_active: bool | None = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

class ServerSchemaUpdate(BaseModel):
    id: uuid.UUID | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    folder_path: str | None = None
    is_active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class ServerSchemaDelete(BaseModel):
    id: uuid.UUID

class ServerSchemaList(BaseModel):
    servers: list[ServerSchemaRead]
