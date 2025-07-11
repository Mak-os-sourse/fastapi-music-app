from sqlalchemy import select, insert, delete

from src.db import session_db
from src.users.models import User
from src.users.schemas import UserDataLogin, UserDataRegist
from src.users.models import User


def add_user(user_data: UserDataRegist):
    stmt = insert(User).values(username=user_data.username, email=user_data.email, password=user_data.password)
    session_db.execute(stmt)
    session_db.commit()

def delete_user(user_data: UserDataLogin):
    stmt = delete(User).where(User.username == user_data.username)
    session_db.execute(stmt)
    session_db.commit()

def get_user(id: int = None, username: str = None) -> object | None:
    if id is None:
        stmt = select(User).where(User.username == username)
    else:
        stmt = select(User).where(User.id == id)
        
    return session_db.scalars(stmt).one_or_none()