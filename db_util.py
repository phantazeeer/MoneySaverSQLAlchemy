import asyncio
from app.db.database import get_session
from app.services.user_service import UserService
from app.services.costs_and_earnings_service import CostsAndEarningsService
from app.db.models.user import create_user_table
from app.db.models.costs_and_earnings import create_costs_and_earnings_table


async def create_all_tables():
    await create_user_table()
    await create_costs_and_earnings_table()


async def drop_all_tables():
    conn = await get_session()
    await conn.execute("""DROP TABLE costs_and_earnings""")
    await conn.execute("""DROP TABLE user""")


async def fill_user_table():
    service = UserService()
    await service.init_session()
    await service.add_user('Максим Струнников', 'ms@gmail.com', '123')
    await service.add_user('Николас Сенченков', 'ns@gmail.com', '123')
    await service.add_user('Дэнис Качалин', 'dk@gmail.com', '123')
    await service.add_user('Ivan Anufriev', 'ia@gmail.com', '123')
    await service.add_user('John Gazon', 'jg@gmail.com', '123')


async def fill_costs_and_earnings_table():
    service = CostsAndEarningsService()
    await service.init_session()
    await service.add_record(1, 1, 500)
    await service.add_record(1, 2, 1500)
    await service.add_record(1, 1, 300, "Купил пирожок в столовой")
    await service.add_record(1, 2, 5000, "Мама дала на обеды")
    await service.add_record(5, 2, 1500)
    await service.add_record(5, 1, 500)
    await service.add_record(5, 2, 350000, "Пришла зарплата")
    await service.add_record(5, 1, 10000, "Штраф за плохую архитектуру проекта")

async def fill_all_tables():
    await fill_user_table()
    await fill_costs_and_earnings_table()


if __name__ == "__main__":
    choice = input('d for delete/c for create/f for fill table:\n')
    if choice in "dD":
        asyncio.run(drop_all_tables())
    elif choice in "cC":
        asyncio.run(create_all_tables())
    elif choice in "fF":
        asyncio.run(fill_all_tables())
    else:
        print('Incorrect input')
