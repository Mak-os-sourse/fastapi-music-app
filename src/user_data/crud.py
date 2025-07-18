from datetime import datetime, timezone

import sqlalchemy.exc
from sqlalchemy import *

def add_activity(session_db, table, music_id: int, user_id: int):
    stmt = insert(table).values(user_id=user_id, music_id=music_id, release_date=datetime.now(timezone.utc).timestamp()).returning(table)

    result = session_db.scalars(stmt).one_or_none()
    session_db.commit()

    return result

def get_activity(session_db, table, offset: int = 0, limit: int = 10, fields: list = None):
    list_where = []

    for i in fields:
        list_where.append(text(i))

    stmt = select(table).offset(offset).limit(limit).where(*list_where)

    result = session_db.scalars(stmt)
    return result.all()

def delete_activity(session_db, table, **where):
    list_where = []
    for key, value in where.items():
        list_where.append(text(f"{key} == '{value}'"))

    stmt = delete(table).where(*list_where)

    result = session_db.scalars(stmt)
    session_db.commit()