from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from models import Post, Board

from services.users import UserService
from services.boards import BoardService
from fastapi import HTTPException, status


class PostService:
    @staticmethod
    async def create_post(
        db: AsyncSession, board_id: int, title: str, content: str, token: str
    ):
        user_id = UserService.get_user_id_from_token(token)
        db_post = Post(
            title=title, content=content, board_id=board_id, author_id=user_id
        )
        try:
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)
            return db_post
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def update_post(
        db: AsyncSession, post_id: int, title: str, content: str, token: str
    ):
        post = await PostService.get_post_from_id(db, post_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if post.author_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to update this post"
            )
        post.title = title
        post.content = content
        try:
            await db.commit()
            await db.refresh(post)
            return post
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int, token: str):
        post = await PostService.get_post_from_id(db, post_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if post.author_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to delete this post"
            )

        post.is_deleted = True

        try:
            await db.commit()
            await db.refresh(post)
            return {"message": "Board successfully deleted"}

        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def get_post_from_id(db: AsyncSession, post_id: int, token: str):
        try:
            statement = select(Post).where(Post.post_id == post_id)
            result = await db.execute(statement)
            post = result.scalars().first()

            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            user_id = UserService.get_user_id_from_token(token)

            if post.author_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            return post

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def get_board_from_post_id(db: AsyncSession, post_id: int, token: str):
        post = await PostService.get_post_from_id(db, post_id, token)
        try:
            statement = select(Board).where(Board.board_id == post.board_id)
            result = await db.execute(statement)
            board = result.scalars().first()

            if not board:
                raise HTTPException(status_code=404, detail="Board not found")
            return board

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB error")

    @staticmethod
    async def get_all_accessible_posts(
        db: AsyncSession, board_id: int, token: str, page: int, size: int
    ):
        user_id = UserService.get_user_id_from_token(token)
        # board = await BoardService.get_board_from_id(db, board_id, token)

        try:
            statement = (
                select(Post)
                .join(Board, Post.board_id == Board.board_id)
                .filter(((Board.creator_id == user_id) | (Board.is_public == True)))
                .limit(size)
                .offset((page - 1) * size)
            )
            result = await db.execute(statement)
            accessible_posts = result.scalars().fetchall()

            # fetchone(), fetchmany(size)를 사용하여 size개의 행을 가져올 수 있음

            return accessible_posts

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB error")
