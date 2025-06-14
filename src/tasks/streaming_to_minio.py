from src.db.uow import UnitOfWork
from src.db.connection import async_session_maker
from src.services.sftp_to_minio import streaming_files_from_sftp_to_minio
from celery import shared_task
import asyncio

@shared_task
def celery_streaming_files():
    """
    Перенос файлов с SFTP-сервера в MinIO
    """
    async def wrapper():
        async with async_session_maker() as session:
            uow = UnitOfWork(session)
            await streaming_files_from_sftp_to_minio(uow)
    asyncio.run(wrapper())

