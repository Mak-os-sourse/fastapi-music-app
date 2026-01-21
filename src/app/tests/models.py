from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.user import User
from src.app.models.music import Music
from src.app.models.playlist import PlayList
from src.app.base import base

class Base(base):
    __tablename__ = "Base"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    