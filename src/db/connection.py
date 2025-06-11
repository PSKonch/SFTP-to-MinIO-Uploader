from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, configure_mappers

from src.config import settings

engine = create_async_engine(settings.POSTGRES_URL, echo=True)
async_session_maker = async_sessionmaker(bind=engine)

async def get_async_session():
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    pass

configure_mappers()
