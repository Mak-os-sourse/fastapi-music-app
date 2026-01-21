from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.config import settings
from src.app.base import base

class Music(base):
    __tablename__ = "Music"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    info: Mapped[str] = mapped_column(String(settings.MAX_LEN_INFO))
    text: Mapped[str] = mapped_column()
    genre: Mapped[str] = mapped_column()
    artists: Mapped[str] = mapped_column()
    date_creation: Mapped[int] = mapped_column()
    duration_sec: Mapped[int] = mapped_column()
    size_file: Mapped[int] = mapped_column()
    is_private: Mapped[bool] = mapped_column()
    
class MusicModel:
    id = "id"
    name = "name"
    info = "info"
    text = "text"
    genre = "genre"
    artists = "artists"
    date_creation = "date_creation"
    duration_sec = "duration_sec"
    size_file = "size_file"
    is_private = "is_private"