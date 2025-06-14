import io
import asyncio

from minio import Minio

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

class AsyncToSyncStreamer(io.RawIOBase):
    """
    Обертка для асинхронного чтения файла
    Необходима из-за ограничений синхронного ввода-вывода в Python
    SFTP работает в асинхронном режиме, а MinIO требует синхронного доступа
    """

    def __init__(self, remote_file, chunk_size=8):
        self.remote_file = remote_file
        self.chunk_size = chunk_size
        self.loop = asyncio.get_event_loop()

    def read(self, size=-1):
        if size == -1:
            size = self.chunk_size
        return self.loop.run_until_complete(self.remote_file.read(size))