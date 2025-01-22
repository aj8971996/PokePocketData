import sys
import os
from pathlib import Path
import typing
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.database.db_config import db_config

async def get_async_db() -> typing.AsyncGenerator[AsyncSession, None]:
    """Async database session dependency for FastAPI"""
    async_session_maker = db_config.get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
