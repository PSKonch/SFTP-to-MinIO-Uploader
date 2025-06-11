import uuid

from src.repositories.base import BaseRepository
from src.models.servers import ServerModel 
from src.schemas.servers import ServerSchemaCreate, ServerSchemaRead, ServerSchemaUpdate, ServerSchemaDelete
from sqlalchemy.ext.asyncio import AsyncSession


class ServerRepository(BaseRepository[ServerModel, ServerSchemaCreate, ServerSchemaRead, ServerSchemaUpdate, ServerSchemaDelete]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_server_by_id(self, server_id: uuid.UUID) -> ServerSchemaRead | None:
        return await self.get_one_or_none(id=server_id)

    async def create_server(self, server: ServerSchemaCreate) -> ServerSchemaRead:
        return await self.add(server)

    async def update_server(self, server_id: uuid.UUID, server: ServerSchemaUpdate) -> None:
        await self.edit(server, id=server_id)

    async def delete_server(self, server_id: uuid.UUID) -> None:
        await self.delete(id=server_id)

    async def get_all_servers(self) -> list[ServerSchemaRead]:
        return await self.get_all()
