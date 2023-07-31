from typing import Callable


from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = (
    "postgresql+asyncpg://developer:devpassword@localhost:25000/developer"
)


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True)

session_create: Callable[[], AsyncSession] = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def get_db() -> AsyncSession:
    db = session_create()
    try:
        yield db
    finally:
        await db.close()
