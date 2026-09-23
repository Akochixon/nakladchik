import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DATABASE_URL

# PostgreSQL protokoli asyncpg ga mosligini ta'minlash
db_url = DATABASE_URL
if db_url and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Async Engine yaratish
engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)

# Async Session Fabrikasi
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)