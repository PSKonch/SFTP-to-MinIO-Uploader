from src.db.uow import UnitOfWork
from src.db.connection import async_session_maker
from src.services.scanner import scan_and_store_files
from celery import shared_task
import asyncio

@shared_task
def celery_scan_servers_for_new_files():
    """
    Сканирование серверов на наличие новых файлов и добавление их в базу данных
    Внутри себя содержит обертку для асинхронной обработки задачи
    """
    async def wrapper():
        async with async_session_maker() as session:
            uow = UnitOfWork(session)
            await scan_and_store_files(uow)
    asyncio.run(wrapper())