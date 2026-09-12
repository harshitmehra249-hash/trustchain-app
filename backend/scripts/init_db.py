"""Database initialization script"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


async def init_db():
    """
    Initialize database tables and create default admin user.
    """
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin user exists
        from sqlalchemy import select
        query = select(User).where(User.email == "admin@trustchain-app.dev")
        result = await session.execute(query)
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            # Create default admin user
            admin_user = User(
                email="admin@trustchain-app.dev",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("Admin@123456"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                is_email_verified=True,
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Default admin user created successfully")
            print("\n" + "="*50)
            print("Default Admin User Created")
            print("="*50)
            print(f"Email: admin@trustchain-app.dev")
            print(f"Password: Admin@123456")
            print("Please change the password immediately!")
            print("="*50 + "\n")
        else:
            logger.info("Admin user already exists")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
