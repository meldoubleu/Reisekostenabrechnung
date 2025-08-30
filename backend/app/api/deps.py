from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
