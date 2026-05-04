from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

engine = create_async_engine(settings.database_url)
log.info("Connecting '%s'", settings.database_url)
session_factory = async_sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def check_db_connection():
    async with session_factory() as session:
        return (await session.execute(text("SELECT 1"))).scalar_one()
