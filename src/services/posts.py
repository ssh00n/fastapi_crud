from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from models import Post, Board

from services.users import UserService
from services.boards import BoardService
from fastapi import HTTPException, status


class PostService:
    @staticmethod
    def create_post(db: Session, board_id: int, title: str, content: str, token: str):
        user_id = UserService.get_user_id_from_token(token)
        db_post = Post(
            title=title, content=content, board_id=board_id, author_id=user_id
        )
        try:
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            return db_post
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    def update_post(db: Session, post_id: int, title: str, content: str, token: str):
        post = PostService.get_post_from_id(db, post_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if post.author_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to update this post"
            )
        post.title = title
        post.content = content
        try:
            db.commit()
            db.refresh(post)
            return post
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    def delete_post(db: Session, post_id: int, token: str):
        post = PostService.get_post_from_id(db, post_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if post.author_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to delete this post"
            )

        post.is_deleted = True

        try:
            db.commit()
            db.refresh(post)
            return {"message": "Board successfully deleted"}

        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    def get_post_from_id(db: Session, post_id: int, token: str):
        try:
            post = db.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            user_id = UserService.get_user_id_from_token(token)

            if post.author_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            return post

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    def get_board_from_post_id(db: Session, post_id: int, token: str):
        post = PostService.get_post_from_id(db, post_id, token)
        try:
            board = db.query(Board).filter(Board.board_id == post.board_id).first()

            if not board:
                raise HTTPException(status_code=404, detail="Board not found")
            return board

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB error")

    @staticmethod
    def get_all_accessible_posts(db: Session, board_id: int, token: str):
        user_id = UserService.get_user_id_from_token(token)
        board = BoardService.get_board_from_id(db, board_id, token)

        try:
            accessible_posts = (
                db.query(Post)
                .join(Board, Post.board_id == Board.board_id)
                .filter(((Board.creator_id == user_id) | (Board.is_public == True)))
                .all()
            )

            return accessible_posts

        except OperationalError:
            raise HTTPException(status_code=500, detail="DB error")
