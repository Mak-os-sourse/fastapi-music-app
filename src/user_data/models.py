from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base

class Likes(Base):
    __tablename__ = "Likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    release_date: Mapped[int] = mapped_column()

class Subscribers(Base):
    __tablename__ = "Subscribers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    release_date: Mapped[int] = mapped_column()

class Listening(Base):
    __tablename__ = "Listening"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    release_date: Mapped[int] = mapped_column()
