from sqlalchemy.orm import Mapped, mapped_column

from src.app.base import base

class PlayList(base):
    __tablename__ = "PlayList"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(default=None)
    music: Mapped[str] = mapped_column()
    artist: Mapped[int] = mapped_column()
    is_private: Mapped[bool] = mapped_column()
    kind: Mapped[str] = mapped_column()
    date_creation: Mapped[int] = mapped_column()

class PlayListModel:
    id = "id"
    title = "title"
    music = "music"
    artist = "artist"
    is_private = "is_private"
    kind = "kind"
    date_creation = "date_creation"