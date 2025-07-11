from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base

class Music(Base):
    __tablename__ = "Music"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(25))
    genre: Mapped[str] = mapped_column()
    author_id: Mapped[int] = mapped_column(String(25))
    info: Mapped[str] = mapped_column(String(50))
    format_file: Mapped[str] = mapped_column()
    listing: Mapped[int] = mapped_column()
    release_date: Mapped[int] = mapped_column()