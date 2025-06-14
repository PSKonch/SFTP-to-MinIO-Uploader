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

async def scan_and_store_files(uow: UnitOfWork):
    """
    Сканирование серверов на наличие новых файлов и добавление их в базу данных

    Args:
        uow (UnitOfWork): Объект подключения к базе данных (контекстный менеджер)
    """
    servers = await uow.servers.get_all_servers() 
    for server in servers:
        try:
            async with asyncssh.connect(
                host=server.host,
                port=server.port,
                username=server.username,
                password=server.password
            ) as conn:
                async with conn.start_sftp_client() as sftp:
                    try:
                        files = await sftp.listdir(server.folder_path)
                    except Exception as e:
                        print(f"[WARN] {server.host}: {e}")  # Ошибка при подключении к SFTP, пропускаем сервер
                        continue
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
    await uow.commit()

