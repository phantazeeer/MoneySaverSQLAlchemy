from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base


class AbstractRepository(ABC):
    @abstractmethod
    async def get_one(self, **kwargs):
        pass

    @abstractmethod
    async def add_one(self, **kwargs):
        pass

    @abstractmethod
    async def delete_by_id(self, instance: Base):
        pass

    @abstractmethod
    async def get_list_by(self, **kwargs):
        pass


class BasicRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(self, **kwargs):
        res = await self.session.execute(select(self.model).filter_by(**kwargs))
        return res.scalar_one()

    async def add_one(self, **kwargs):
        stmt = insert(self.model).values(**kwargs).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete_by_id(self, id: int):
        stmt = delete(self.model).where(self.model.id == id).returning(self.model)
        res = await self.session.execute(stmt)
        res = res.scalar_one()
        return res

    async def get_list_by(self, **kwargs):
        res = await self.session.execute(select(self.model).filter_by(**kwargs))
        return res.scalars()
