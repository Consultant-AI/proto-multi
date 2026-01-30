"""Database connection management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import text
from redis.asyncio import Redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)


# SQLAlchemy Base
class Base(DeclarativeBase):
    pass


# Ensure URL uses asyncpg driver
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Async engine for PostgreSQL
engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Redis client
redis_client: Redis | None = None


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """Dependency for getting Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = await Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Import models to register them with Base
        from app.db import models  # noqa: F401

        async with engine.begin() as conn:
            # Test connection
            await conn.execute(text("SELECT 1"))
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database connection established and tables created")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
    await engine.dispose()
    logger.info("👋 Database connections closed")
