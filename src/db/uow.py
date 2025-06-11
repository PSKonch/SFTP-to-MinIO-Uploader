from src.db.connection import async_session_maker
from src.repositories.files import FileRepository
from src.repositories.servers import ServerRepository


class UnitOfWork:
    def __init__(self, session: async_session_maker): # type: ignore
        self.session = session
        self.files = FileRepository(session)
        self.servers = ServerRepository(session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()