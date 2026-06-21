from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Create the async SQLAlchemy engine using the configured database URL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"ssl": "require"},
)


# Create a session factory for generating AsyncSession instances
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass


# FastAPI dependency that provides a database session per request
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session