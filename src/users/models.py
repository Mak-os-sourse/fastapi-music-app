from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, engine

class User(Base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    
    def __repr__(self):
        return f'User(id = {self.id}, username = {self.username}, email = {self.email}, password = {self.password})'

Base.metadata.create_all(engine)