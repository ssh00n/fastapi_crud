from sqlalchemy import desc
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session
from schemas import BoardBaseSchema, BoardCreateSchema, BoardSchema
from models import User, Board, Post

from services.users import UserService

from fastapi import HTTPException, status


class BoardService:
    @staticmethod
    def create_board(db: Session, name: str, public: bool, token: str):
        try:
            user_id = UserService.get_user_id_from_token(token)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = UserService.get_user_from_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        is_present = BoardService.get_board_from_name(db, name)
        if is_present:
            raise HTTPException(status_code=400, detail="Board already exists")

        db_board = Board(
            name=name,
            is_public=public,
            creator_id=user_id,
        )
        db.add(db_board)
        db.commit()
        db.refresh(db_board)
        return db_board

    @staticmethod
    def update_board(db: Session, board_id: int, name: str, public: bool, token: str):
        board = BoardService.get_board_from_id(db, board_id, token)

        user_id = UserService.get_user_id_from_token(token)
        # user_id를 통해 해당 유저가 생성한 게시판인지 확인
        if board.creator_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to update this board"
            )

        board.name = name
        board.is_public = public

        db.commit()
        db.refresh(board)

        return board

    @staticmethod
    def delete_board(db: Session, board_id: int, token: str):
        board = BoardService.get_board_from_id(db, board_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if board.creator_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to delete this board"
            )
        # Soft delete
        board.is_deleted = True
        db.commit()

        return {"message": "Board successfully deleted"}

    @staticmethod
    def get_board_from_id(db: Session, board_id: int, token: str):
        board = db.query(Board).filter(Board.board_id == board_id).first()

        if not board:
            raise HTTPException(status_code=404, detail="Board not found")

        user_id = UserService.get_user_id_from_token(token)

        if board.creator_id != user_id and not board.is_public:
            raise HTTPException(status_code=403, detail="Access denied")

        return board

    @staticmethod
    def get_board_from_name(db: Session, name=str):
        return db.query(Board).filter(Board.name == name).first()

    @staticmethod
    def get_all_accessible_boards(db: Session, token: str):
        user_id = UserService.get_user_id_from_token(token)

        accessible_boards = (
            db.query(Board)
            .filter((Board.creator_id == user_id) | (Board.is_public == True))
            .subquery()
        )

        sorted_boards = (
            db.query(accessible_boards.c.board_id, func.count(Post.post_id))
            .join(Post, Post.board_id == accessible_boards.c.board_id)
            .group_by(accessible_boards.c.board_id)
            .order_by(desc(func.count(Post.post_id)))
            .all()
        )

        return sorted_boards

    @staticmethod
    def list_board():
        pass

    @staticmethod
    def is_creator_board(db: Session, user_id: int):
        pass
