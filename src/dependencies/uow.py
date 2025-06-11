from typing import Annotated

from fastapi import Depends

from src.db.connection import get_async_session
from src.db.uow import UnitOfWork


UoW = Annotated[UnitOfWork, Depends(get_async_session)]