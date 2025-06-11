import uuid

from src.repositories.base import BaseRepository
from src.models.files import FileModel
from src.schemas.files import FileSchemaCreate, FileSchemaRead, FileSchemaUpdate, FileSchemaDelete
from sqlalchemy.ext.asyncio import AsyncSession

class FileRepository(BaseRepository[FileModel, FileSchemaCreate, FileSchemaRead, FileSchemaUpdate, FileSchemaDelete]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_file_by_id(self, file_id: uuid.UUID) -> FileSchemaRead | None:
        return await self.get_one_or_none(id=file_id)

    async def create_file(self, file: FileSchemaCreate) -> FileSchemaRead:
        return await self.add(file)

    async def update_file(self, file_id: uuid.UUID, file: FileSchemaUpdate) -> None:
        await self.edit(file, id=file_id)

    async def delete_file(self, file_id: uuid.UUID) -> None:
        await self.delete(id=file_id)

    async def get_all_files(self) -> list[FileSchemaRead]:
        return await self.get_all()