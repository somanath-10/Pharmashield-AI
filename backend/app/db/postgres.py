import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

Base = declarative_base()

# Default to sqlite if no postgres url is provided (useful for tests if needed)
SQLALCHEMY_DATABASE_URL = settings.postgres_url or "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_postgres_db():
    logger.info("Initializing PostgreSQL database...")
    async with engine.begin() as conn:
        # For MVP we just use create_all, in production we would use alembic
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL tables created successfully.")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
