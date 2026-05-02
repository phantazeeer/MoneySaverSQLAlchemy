import os
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import *

DB_PATH = "./db_for_integration_test"
DB_URL = "sqlite+aiosqlite:///" + DB_PATH

engine = create_async_engine(DB_URL)
_session_maker = async_sessionmaker(engine, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with _session_maker() as _session:
        yield _session


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
    session = await anext(sess_gen)
    yield session
    await session.close()
    await sess_gen.aclose()
