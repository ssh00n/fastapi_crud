from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String)
    hash_password = Column(String)
    is_logged_in = Column(Boolean, default=False)

    boards = relationship("Board", back_populates="creator")

    posts = relationship("Post", back_populates="author")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_public = Column(Boolean, default=True)

    # user - board
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="boards")

    # board - post
    posts = relationship("Post", back_populates="board")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

    # user - post
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    # board - post
    board_id = Column(Integer, ForeignKey("boards.id"))
    board = relationship("Board", back_populates="posts")
