from typing import Callable
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

session_create: Callable[[], AsyncSession] = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def get_db() -> AsyncSession:
    db = session_create()
    try:
        yield db
    finally:
        await db.close()
