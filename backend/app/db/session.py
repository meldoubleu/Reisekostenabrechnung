from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from ..core.config import settings
from ..core.logging import logger

# Use async driver if postgres, else assume sqlite+aiosqlite
DATABASE_URL = settings.database_url

logger.info(f"Initializing database with URL: {DATABASE_URL}")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Initialize database tables and verify connection."""
    try:
        logger.info("Starting database initialization...")
        
        # Import models so they are registered with Base
        from ..models import travel  # noqa: F401
        from ..models import user    # noqa: F401

        async with engine.begin() as conn:
            # ensure db is reachable
            logger.info("Testing database connection...")
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            # create tables (MVP, no migrations)
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
