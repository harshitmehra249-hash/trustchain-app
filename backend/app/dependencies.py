"""Database dependency"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from app.main import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
