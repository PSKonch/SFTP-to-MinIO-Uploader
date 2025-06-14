from typing import Annotated

from fastapi import Depends

from src.db.connection import get_async_session
from src.db.uow import UnitOfWork

async def get_uow(session = Depends(get_async_session)):
    async with UnitOfWork(session) as uow:
        yield uow

UoW = Annotated[UnitOfWork, Depends(get_uow)]