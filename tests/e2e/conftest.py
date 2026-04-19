from typing import AsyncGenerator

import pytest
import os
from app.db.models import *
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert
from app import create_app
from app.utils.dependencies import get_sqlalchemy_session
from httpx import AsyncClient, ASGITransport
from app.utils.passwords import get_password_hash

DB_PATH = "./db_for_e2e_test"
DB_URL = "sqlite+aiosqlite:///" + DB_PATH

engine = create_async_engine(DB_URL)
_session_maker = async_sessionmaker(engine, class_=AsyncSession)


def get_session():
    return _session_maker


app = create_app()
app.dependency_overrides[get_sqlalchemy_session] = get_session


@pytest_asyncio.fixture(scope="session")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


@pytest_asyncio.fixture(scope="function")
async def ready_session(create_tables):
    sess_gen = get_session()
    session = sess_gen()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def user_ids(create_tables):
    sess_gen = get_session()
    session = sess_gen()
    try:
        users_data = [
            ('Максим Струнников', 'ms@gmail.com', '123'),
            ('Николас Сенченков', 'ns@gmail.com', '123'),
            ('Дэнис Качалин', 'dk@gmail.com', '123'),
            ('Ivan Anufriev', 'ia@gmail.com', '123'),
            ('John Gazon', 'jg@gmail.com', '123'),
        ]
        users = []
        for name, email, raw_pwd in users_data:
            stmt = insert(User).values(
                username=name,
                email=email,
                password=get_password_hash(raw_pwd)
            ).returning(User.id)
            result = await session.execute(stmt)
            user_id = result.scalar_one()
            users.append(user_id)
        await session.commit()
        await session.close()
        return users
    finally:
        await session.close()



@pytest_asyncio.fixture(scope="session", autouse=True)
async def fill_costs_and_earnings_table(user_ids):
    sess_gen = get_session()
    session = sess_gen()
    max_id = user_ids[0]
    john_id = user_ids[4]
    try:
        records = [
            (max_id, 1, 500, None),
            (max_id, 0, 1500, None),
            (max_id, 1, 300, "Купил пирожок в столовой"),
            (max_id, 0, 5000, "Мама дала на обеды"),
            (john_id, 0, 1500, None),
            (john_id, 1, 500, None),
            (john_id, 0, 350000, "Пришла зарплата"),
            (john_id, 1, 10000, "Штраф за плохую архитектуру проекта"),
        ]
        for user_id, op_type, value, comment in records:
            stmt = insert(CostsAndEarnings).values(
                user_id=user_id,
                operation_type=op_type,
                value=value,
                comment=comment
            )
            await session.execute(stmt)
        await session.commit()
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def unlogged_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as _unlogged_client:
        yield _unlogged_client


@pytest_asyncio.fixture(scope="session")
async def logged_client(client):
    users_cred = {"email": "ms@gmail.com",
                  "password": "123"}
    user = await client.post("/user/login", data=users_cred)
    cookie = user.cookies["Authorization"]
    client.cookies.set("Authorization", cookie)
    return client
