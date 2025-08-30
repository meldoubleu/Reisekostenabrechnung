from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from ..core.config import settings

# Use async driver if postgres, else assume sqlite+aiosqlite
DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def init_db():
    # Import models so they are registered with Base
    from ..models import travel  # noqa: F401
    from ..models import user    # noqa: F401

    async with engine.begin() as conn:
        # ensure db is reachable
        await conn.execute(text("SELECT 1"))
        # create tables (MVP, no migrations)
        await conn.run_sync(Base.metadata.create_all)
