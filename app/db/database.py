from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.config import settings
from app.utils.logger import get_logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

log = get_logger(__name__)

engine = create_async_engine(settings.database_url)
log.info("Connecting '%s'", settings.database_url)
session_factory = async_sessionmaker(engine, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session
