from src.db.connection import async_session_maker, get_async_session
from src.repositories.files import FileRepository
from src.repositories.servers import ServerRepository


class UnitOfWork:
    def __init__(self, session: get_async_session()): # type: ignore
        self.session = session
        self.files = FileRepository(session)
        self.servers = ServerRepository(session)

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()