import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.repositories.base import BaseRepository
from src.models.files import FileModel, FileStatus
from src.schemas.files import FileSchemaCreate, FileSchemaRead, FileSchemaUpdate, FileSchemaDelete
from sqlalchemy.ext.asyncio import AsyncSession

class FileRepository(BaseRepository):
    model = FileModel
    schema = FileSchemaRead

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
        stmt = select(FileModel).options(selectinload(FileModel.server))
        result = await self.session.execute(stmt)
        files = result.scalars().all()
        return [FileSchemaRead.model_validate(file) for file in files]
    
    async def get_pending_files(self):
        query = select(FileModel).where(FileModel.status == FileStatus.PENDING)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def take_a_file_to_put_in_minio(self, file_id: uuid.UUID) -> FileSchemaRead | None:
        query = (
            update(FileModel)
            .where(
                FileModel.id == file_id,
                FileModel.status.in_([FileStatus.PENDING, FileStatus.ERROR])
            )
            .values(status=FileStatus.DOWNLOADING)
            .returning(FileModel)
        )
        result = await self.session.execute(query)
        file = result.scalar_one_or_none()
        await self.session.commit()
        if file:
            return file  
        return None      