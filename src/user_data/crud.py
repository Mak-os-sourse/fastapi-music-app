from sqlalchemy import *

from src.user_data.models import *

def add_activity(session_db, table: str, music_id: int, user_id: int):
    stmt = insert(table).values(user_id=user_id, music_id=music_id).returning(table)

    result = session_db.scalars()
    return result.one_or_none()

def get_activity(session_db, table: str, user_id: int):
    stmt = select(table).where(user_id == "user_id")

    result = session_db.scalars()
    return result.one_or_none()

def delete_activity(session_db, table: str, user_id: int = None, music_id: int = None):
    stmt = delete(table).where("user_id" == user_id, music_id == "music_id")

    result = session_db.scalars()
    return result.one_or_none()