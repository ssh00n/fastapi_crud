from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.ext.asyncio import AsyncEngine
from database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fullname = Column(String, index=True, nullable=False)
    email = Column(String, nullable=False)
    hash_password = Column(String)
    is_logged_in = Column(Boolean, default=False)
    boards = relationship("Board", back_populates="creator")
    posts = relationship("Post", back_populates="author")


class Board(Base):
    __tablename__ = "boards"

    board_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, unique=True)
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    # user - board
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="boards")
    # board - post
    posts = relationship("Post", back_populates="board")


class Post(Base):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    content = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    is_deleted = Column(Boolean, default=False)
    # user - post
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    # board - post
    board_id = Column(Integer, ForeignKey("boards.board_id"))
    board = relationship("Board", back_populates="posts")


async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
