import io
import asyncssh

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.db.uow import UnitOfWork
from src.models.files import FileStatus
from src.minio import minio_client
from src.schemas.files import FileSchemaRead
from src.services.notifier import notify_about_streaming_file

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type((asyncssh.Error, OSError, IOError, ConnectionError))
)
async def _download_and_upload_file_inner(uow: UnitOfWork, file: FileSchemaRead, minio_client):
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
                await notify_about_streaming_file(file.file_path)
                await uow.commit()
    finally:
        if remote_file:
            await remote_file.close()

async def download_and_upload_file(uow: UnitOfWork, file: FileSchemaRead, minio_client):
    """
    Качает один файл с SFTP и заливает его в MinIO, меняет статус
    Добавлены ретраи и обработка ошибок
    """
    try:
        await _download_and_upload_file_inner(uow, file, minio_client)
    except Exception as e:
        await uow.files.edit({"id": file.id}, {"status": FileStatus.ERROR})
        await uow.commit()
        print(f"[ERROR] {file.file_name}: {e}")

async def streaming_files_from_sftp_to_minio(uow: UnitOfWork, minio_client):
    """
    Переносит все PENDING и ERROR файлы с SFTP в MinIO
    """
    files = await uow.files.get_all_files()
    for file in files:
        if file.status in (FileStatus.PENDING, FileStatus.ERROR):
            await download_and_upload_file(uow, file, minio_client)

async def stream_file_from_sftp_to_minio(uow: UnitOfWork, file_id: str, minio_client):
    """
    Переносит конкретный файл по id с SFTP в MinIO
    """
    file = await uow.files.take_a_file_to_put_in_minio(file_id)
    if file:
        await download_and_upload_file(uow, file, minio_client)