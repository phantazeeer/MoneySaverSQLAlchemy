from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(settings.database_url)
print(f"Connecting '{settings.database_url}'")
session_factory = async_sessionmaker(engine, class_=AsyncSession)

async def get_async_session():
    async with session_factory() as session:
        yield session
