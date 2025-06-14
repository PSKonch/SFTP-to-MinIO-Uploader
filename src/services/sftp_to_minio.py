import io
import asyncssh

from src.db.uow import UnitOfWork
from src.models.files import FileStatus
from src.services.minio import minio_client
import io

async def streaming_files_from_sftp_to_minio(uow: UnitOfWork):
    """
    Перенос файлов с SFTP-сервера в MinIO

    Args:
        uow (UnitOfWork): Объект подключения к базе данных (контекстный менеджер)
    """
    files = await uow.files.get_all_files()
    for file in files:
        if file.status == FileStatus.PENDING or file.status == FileStatus.ERROR:
            remote_file = None
            try:
                await uow.files.edit({"id": file.id}, {"status": FileStatus.DOWNLOADING})
                await uow.commit()
                async with asyncssh.connect(
                    host=file.server.host,
                    port=file.server.port,
                    username=file.server.username,
                    password=file.server.password
                ) as conn:
                    async with conn.start_sftp_client() as sftp:
                        remote_file = await sftp.open(file.file_path, 'rb')
                        content = b""
                        while True:
                            chunk = await remote_file.read(1024 * 1024)
                            if not chunk:
                                break
                            content += chunk
                        minio_client.put_object(
                            bucket_name="files",
                            object_name=file.file_name,
                            data=io.BytesIO(content),
                            length=len(content),
                            part_size=10 * 1024 * 1024
                        )
                        await uow.files.edit({"id": file.id}, {"status": FileStatus.DOWNLOADED})
                        await uow.commit()
            except Exception as e:
                await uow.files.edit({"id": file.id}, {"status": FileStatus.ERROR})
                await uow.commit()
            finally:
                if remote_file:
                    await remote_file.close()
