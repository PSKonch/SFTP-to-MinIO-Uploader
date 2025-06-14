from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

class BaseRepository:
    model = None
    schema = None

    def __init__(self, session):
        self.session = session


    async def get_filtered(self, *filter, **filter_by):
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [self.schema.from_orm(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, *filters, **filter_by):
        query = select(self.model).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().first() 
        return self.schema.from_orm(model) if model else None

    async def add(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalars().one()
        return self.schema.from_orm(model)
    
    async def edit(self, filter_by: dict, data: dict) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data)
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)

    async def update(self, *filters, **values):
        query = (
            update(self.model)
            .filter(*filters)
            .values(**values)
        )
        await self.session.execute(query)