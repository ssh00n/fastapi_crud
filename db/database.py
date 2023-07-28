from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql:developer:devpassword@localhost:25000/developer"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
