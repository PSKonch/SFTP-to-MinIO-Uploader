from fastapi import APIRouter

from src.dependencies.uow import UoW
from src.schemas.files import FileSchemaCreate, FileSchemaUpdate

router = APIRouter()

@router.post("/files/")
async def create_file(file: FileSchemaCreate, uow: UoW):
    return await uow.files.create(file)

@router.get("/files/")
async def list_files(uow: UoW):
    return await uow.files.list()

@router.get("/files/{file_id}")
async def get_file(file_id: int, uow: UoW):
    return await uow.files.get(file_id)

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, uow: UoW):
    return await uow.files.delete(file_id)

@router.put("/files/{file_id}")
async def update_file(file_id: int, file: FileSchemaUpdate, uow: UoW):
    return await uow.files.update(file_id, file)
