import asyncio
from app.db.database import get_session
from app.db.models.user import create_user_table
from app.db.models.costs_and_earnings import create_costs_and_earnings_table


async def create_all_tables():
    await create_user_table()
    await create_costs_and_earnings_table()


async def drop_all_tables():
    conn = await get_session()
    await conn.execute("""DROP TABLE costs_and_earnings""")
    await conn.execute("""DROP TABLE user""")


if __name__ == "__main__":
    choice = input('d for delete/c for create:\n')
    if choice in "dD":
        asyncio.run(drop_all_tables())
    elif choice in "cC":
        asyncio.run(create_all_tables())
    else:
        print('Incorrect input')
