from fastapi import APIRouter

from src.dependencies.uow import UoW
from src.schemas.servers import ServerSchemaCreate, ServerSchemaUpdate

router = APIRouter()

@router.post("/servers/")
async def create_server(server: ServerSchemaCreate, uow: UoW):
    return await uow.servers.create(server)

@router.get("/servers/")
async def list_servers(uow: UoW):
    return await uow.servers.list()

@router.get("/servers/{server_id}")
async def get_server(server_id: int, uow: UoW):
    return await uow.servers.get(server_id)

@router.delete("/servers/{server_id}")
async def delete_server(server_id: int, uow: UoW):
    return await uow.servers.delete(server_id)

@router.put("/servers/{server_id}")
async def update_server(server_id: int, server: ServerSchemaUpdate, uow: UoW):
    return await uow.servers.update(server_id, server)
