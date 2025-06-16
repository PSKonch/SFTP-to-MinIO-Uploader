import asyncssh

from src.db.uow import UnitOfWork
from src.schemas.servers import ServerSchemaRead
from src.schemas.files import FileSchemaCreate
from src.models.files import FileStatus

async def get_file_checksum(sftp, file_path):
    """
    Получение контрольной суммы файла по его пути. Доделать в будущем
    Необходима для проверки целостности файлов при загрузке в MinIO и оригинальности

    Args:
        sftp: Подключение к SFTP-серверу
        file_path: Путь к файлу на SFTP-сервере

    Returns:
        checksum: Контрольная сумма файла
    """
    return None  # Доделать в будущем

async def scan_files_on_server(uow: UnitOfWork, server: ServerSchemaRead):
    """
    Сканирует конкретный сервер и сохраняет новые файлы в БД
    """
    try:
        async with asyncssh.connect(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            known_hosts=None
        ) as conn:
            async with conn.start_sftp_client() as sftp:
                try:
                    files = await sftp.listdir(server.folder_path)
                except Exception as e:
                    print(f"[WARN] {server.host}: {e}")
                    return
                for file_name in files:
                    file_path = f"{server.folder_path}/{file_name}"
                    file_stat = await sftp.stat(file_path)
                    exists = await uow.files.get_filtered(
                        server_id=server.id,
                        file_name=file_name
                    )
                    if not exists:
                        file_obj = FileSchemaCreate(
                            server_id=server.id,
                            file_path=file_path,
                            file_name=file_name,
                            file_size=file_stat.size,
                            checksum=None,
                            status=FileStatus.PENDING,
                            minio_key=None,
                            error_message=None,
                        )
                        await uow.files.create_file(file_obj)
    except Exception as e:
        print(f"[ERROR] SFTP SCAN {server.host}:{server.port}: {e}")

async def scan_and_store_files(uow: UnitOfWork):
    """
    Сканирование всех серверов на наличие новых файлов
    """
    servers = await uow.servers.get_all_servers()
    for server in servers:
        await scan_files_on_server(uow, server)
    await uow.commit()

async def scan_server(uow: UnitOfWork, server_id: str):
    """
    Сканирует сервер по id
    """
    server = await uow.servers.get_server_by_id(server_id)
    if not server:
        return
    await scan_files_on_server(uow, server)
    await uow.commit()