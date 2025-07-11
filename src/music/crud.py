from sqlalchemy import *
from datetime import datetime, timezone

from src.music.models import Music

def add_music(session_db, user_id: int, title: str, genre: str, info: str) -> Music:
    stmt = insert(Music).values(title=title,
                                genre=genre,
                                author_id=user_id,
                                info=info,
                                release_date=datetime.now(timezone.utc).timestamp(),
                                listing=0).returning(Music)
    result = session_db.scalars(stmt).one_or_none()
    session_db.commit()
    return result

def get_music(session_db,
              where: list,
              offset: int = 0,
              limit: int = 10,
              sorting: list[tuple[str, bool]] = None,
              ) -> list[Music] | None:
    if where == []:
        where.append(1 == 1)

    sorting_fields = []

    for i in sorting:
        field = i[0]
        reverse = i[1]
        if reverse is True:
            sorting_fields.append(asc(field))
        if reverse is False:
            sorting_fields.append(desc(field))

    if sorting_fields != []:
        stmt = select(Music).order_by(*sorting_fields).where(text(*where)).limit(limit).offset(offset)
    else:
        stmt = select(Music).where(*where).limit(limit).offset(offset)

    data = session_db.scalars(stmt)
    return data.fetchall()

def change_user_music(session_db, id: int, title: str = None, genre: str = None, info: str = None):
    list_args = {"title": title, "genre": genre, "info": info}
    value_music = {}

    for key, value in list_args.items():
        if value is not None:
            value_music[key] = value

    stmt = update(Music).where(Music.id == id).values(**value_music)

    session_db.execute(stmt)
    session_db.commit()

def delete_user_music(session_db, id: int, author_id: int) -> None:
    stmt = delete(Music).where(Music.id == id, Music.author_id == author_id)

    session_db.execute(stmt)
    session_db.commit()