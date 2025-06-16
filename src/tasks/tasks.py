import dramatiq
import asyncio

from dramatiq_crontab import cron

from src.minio import minio_client
from src.services.scanner import scan_server
from src.services.sftp_to_minio import stream_file_from_sftp_to_minio
from src.db.connection import async_session_maker
from src.db.uow import UnitOfWork

@dramatiq.actor
def scan_server_task(server_id: str):
    async def run():
        async with async_session_maker() as session:
            async with UnitOfWork(session) as uow:
                await scan_server(uow, server_id)
    asyncio.run(run())

@dramatiq.actor
def stream_file_task(file_id: str):
    async def run():
        async with async_session_maker() as session:
            async with UnitOfWork(session) as uow:
                await stream_file_from_sftp_to_minio(uow, file_id, minio_client)
    asyncio.run(run())

@dramatiq.actor
def scan_all_servers_task():
    async def main():
        async with async_session_maker() as session:
            async with UnitOfWork(session) as uow:
                servers = await uow.servers.get_all_servers()
                for server in servers:
                    scan_server_task.send(str(server.id))
    asyncio.run(main())

@dramatiq.actor
def stream_all_files_task():
    async def main():
        async with async_session_maker() as session:
            async with UnitOfWork(session) as uow:
                files = await uow.files.get_all_files()
                for file in files:
                    stream_file_task.send(str(file.id))
    asyncio.run(main())
