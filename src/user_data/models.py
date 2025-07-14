from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base

class Likes(Base):
    __tablename__ = "Likes"

    music_id: Mapped[str] = mapped_column()
    user_id: Mapped[str] = mapped_column()
    release_data: Mapped[str] = mapped_column()

class Favorites(Base):
    __tablename__ = "Favorites"

    music_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    release_data: Mapped[int] = mapped_column()

class Listening(Base):
    __tablename__ = "Listening"

    music_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    release_data: Mapped[int] = mapped_column()