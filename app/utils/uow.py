from abc import ABC, abstractmethod
from app.db.database import AsyncSession
from app.repositories.costs_and_earnings_repo import CostsAndEarningsRepository
from app.repositories.user_repo import UserRepository
from app.repositories.category_repo import CategoryRepository


class IUnitOfWork(ABC):
    session: AsyncSession = None
    users: UserRepository
    records: CostsAndEarningsRepository
    category: CategoryRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        await self.session.commit()

    @abstractmethod
    async def rollback(self):
        await self.session.rollback()


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.records = CostsAndEarningsRepository(self.session)
        self.categories = CategoryRepository(self.session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

        if exc_type:
            # print(type(exc_type), type(exc_val), type(exc_tb))
            # print(exc_type, exc_val, exc_tb)
            raise exc_type(exc_val)

    async def commit(self):
        await super().commit()

    async def rollback(self):
        await super().rollback()