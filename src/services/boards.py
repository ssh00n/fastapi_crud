from sqlalchemy import desc, select
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import BoardBaseSchema, BoardCreateSchema, BoardSchema, PostSchema
from models import User, Board, Post

from services.users import UserService

from fastapi import HTTPException, status


class BoardService:
    @staticmethod
    async def create_board(db: AsyncSession, name: str, public: bool, token: str):
        user_id = UserService.get_user_id_from_token(token)
        print(f"user_id: {user_id}")
        user = await UserService.get_user_from_id(db, user_id)
        print(f"user: {user}")
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        is_present = await BoardService.get_board_from_name(db, name)
        if is_present:
            raise HTTPException(status_code=400, detail="Board already exists")

        db_board = Board(
            name=name,
            is_public=public,
            creator_id=user_id,
        )
        print(f"db_board: {db_board}")

        try:
            db.add(db_board)
            await db.commit()
            await db.refresh(db_board)

            return BoardSchema(
                name=db_board.name,
                is_public=db_board.is_public,
                board_id=db_board.board_id,
                creator_id=db_board.creator_id,
            )
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

        except Exception as e:
            print("Validation Error!!!!!!!!!!!!!")
            print(e)

    @staticmethod
    async def update_board(
        db: AsyncSession, board_id: int, name: str, public: bool, token: str
    ):
        board = await BoardService.get_board_from_id(db, board_id, token)

        user_id = UserService.get_user_id_from_token(token)
        # user_id를 통해 해당 유저가 생성한 게시판인지 확인
        if board.creator_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to update this board"
            )

        board.name = name
        board.is_public = public

        try:
            await db.commit()
            await db.refresh(board)
            return BoardSchema(
                name=board.name,
                is_public=board.is_public,
                board_id=board.board_id,
                creator_id=board.creator_id,
            )
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def delete_board(db: AsyncSession, board_id: int, token: str):
        board = await BoardService.get_board_from_id(db, board_id, token)

        user_id = UserService.get_user_id_from_token(token)
        if board.creator_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not allowed to delete this board"
            )
        # Soft delete
        board.is_deleted = True

        try:
            await db.commit()
            await db.refresh(board)
            return {"message": "Board successfully deleted"}
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    async def get_board_from_id(db: AsyncSession, board_id: int, token: str):
        statement = select(Board).where(Board.board_id == board_id)
        result = await db.execute(statement)
        board = result.scalars().first()

        if not board:
            raise HTTPException(status_code=404, detail="Board not found")

        user_id = UserService.get_user_id_from_token(token)

        if board.creator_id != user_id and not board.is_public:
            raise HTTPException(status_code=403, detail="Access denied")

        return BoardSchema(
            name=board.name,
            is_public=board.is_public,
            board_id=board.board_id,
            creator_id=board.creator_id,
        )

    @staticmethod
    async def get_board_from_name(db: AsyncSession, name=str):
        try:
            statement = select(Board).where(Board.name == name)
            result = await db.execute(statement)
            return result.scalars().first()
        except OperationalError:
            raise HTTPException(status_code=500, detail="Database connection error")

    @staticmethod
    async def get_all_accessible_boards(db: AsyncSession, token: str):
        user_id = UserService.get_user_id_from_token(token)

        try:
            accessible_boards = (
                select(Board.board_id)
                .where((Board.creator_id == user_id) | (Board.is_public == True))
                .subquery()
            )

            sorted_boards = (
                select(Board, func.count(Post.post_id))
                .outerjoin_from(Board, Post, Post.board_id == Board.board_id)
                .join_from(
                    Board,
                    accessible_boards,
                    Board.board_id == accessible_boards.c.board_id,
                )
                .group_by(Board)
                .order_by(desc(func.count(Post.post_id)))
            )

            result = await db.execute(sorted_boards)

            board_list = result.fetchall()

            return [
                BoardSchema(
                    name=board.name,
                    is_public=board.is_public,
                    is_deleted=board.is_deleted,
                    board_id=board.board_id,
                    creator_id=board.creator_id,
                )
                for board, _ in board_list
            ]

        except OperationalError as e:
            raise HTTPException(status_code=500, detail="DB Error")

    @staticmethod
    def list_board():
        pass

    @staticmethod
    def is_creator_board(db: AsyncSession, user_id: int):
        pass
