import asyncio

from app.db.database import session_factory
from app.services.costs_and_earnings_service import CostsAndEarningsService
from app.services.user_service import UserService
from app.utils.uow import UnitOfWork


async def fill_user_table():
    service = UserService(UnitOfWork(session_factory))
    await service.add_user('Максим Струнников', 'ms@gmail.com', '123')
    await service.add_user('Николас Сенченков', 'ns@gmail.com', '123')
    await service.add_user('Дэнис Качалин', 'dk@gmail.com', '123')
    await service.add_user('Ivan Anufriev', 'ia@gmail.com', '123')
    await service.add_user('John Gazon', 'jg@gmail.com', '123')


async def fill_costs_and_earnings_table():
    service = CostsAndEarningsService(UnitOfWork(session_factory))
    await service.add_record(1, 1, 500)
    await service.add_record(1, 0, 1500)
    await service.add_record(1, 1, 300, "Купил пирожок в столовой")
    await service.add_record(1, 0, 5000, "Мама дала на обеды")
    await service.add_record(5, 0, 1500)
    await service.add_record(5, 1, 500)
    await service.add_record(5, 0, 350000, "Пришла зарплата")
    await service.add_record(5, 1, 10000, "Штраф за плохую архитектуру проекта")


async def fill_all_tables():
    await fill_user_table()
    await fill_costs_and_earnings_table()


if __name__ == "__main__":
    asyncio.run(fill_all_tables())
