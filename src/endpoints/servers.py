from fastapi import APIRouter

from src.dependencies.uow import UoW
from src.schemas.servers import ServerSchemaCreate, ServerSchemaUpdate
from src.services.scanner import scan_and_store_files
from src.services.sftp_to_minio import streaming_files_from_sftp_to_minio

router = APIRouter(prefix="/servers", tags=["servers"])

async def test_sftp_connection(host, port, username, password):
    """
    Эндпоинт для проверки подключения к SFTP-серверу

    Args:
        host (str): Хост SFTP-сервера
        port (int): Порт SFTP-сервера
        username (str): Имя пользователя для подключения
        password (str): Пароль для подключения

    Returns:
        bool: Результат проверки подключения
    """
    import asyncssh
    try:
        async with asyncssh.connect(host, port=port, username=username, password=password) as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.listdir('.') 
        return True
    except Exception as e:
        return False

@router.post("/nt/")
async def create_server(server: ServerSchemaCreate, uow: UoW):
    """
    Внесение нового сервера в пул подключений

    Args:
        server (ServerSchemaCreate): Данные сервера для создания подключения и добавления в пул серверов
        uow (UoW): Объект единицы работы для доступа к базе данных

    Returns:
        result (ServerSchemaRead): Данные добавленного сервера
    """
    is_ok = await test_sftp_connection(
        server.host, server.port, server.username, server.password
    )
    if not is_ok:
        return {"error": "Invalid SFTP credentials"}, 400
    result = await uow.servers.create_server(server)
    await uow.commit()
    return result

@router.post("/to_minio/")
async def stream_files_to_minio(uow: UoW):
    """
    Потоковая передача файлов с SFTP-сервера в MinIO

    Args:
        server (ServerSchemaCreate): Данные сервера для создания подключения
        uow (UoW): Объект единицы работы для доступа к базе данных

    Returns:
        result (ServerSchemaRead): Данные добавленного сервера
    """
    await streaming_files_from_sftp_to_minio(uow)

@router.post("/scan_files")
async def scan_files_endpoint(uow: UoW):
    """
    Ручное сканирование файлов на SFTP-сервере и их добавление в базу данных
    """
    await scan_and_store_files(uow)
    return {"status": "ok"}

@router.get("/{server_id}")
async def get_server(server_id: str, uow: UoW):
    return await uow.servers.get_server_by_id(server_id)

@router.delete("/{server_id}")
async def delete_server(server_id: str, uow: UoW):
    return await uow.servers.delete_server(server_id)

@router.put("/{server_id}")
async def update_server(server_id: str, server: ServerSchemaUpdate, uow: UoW):
    return await uow.servers.update_server(server_id, server)

@router.get("/")
async def list_servers(uow: UoW):
    return await uow.servers.get_all_servers()