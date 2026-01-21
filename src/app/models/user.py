from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.config import settings
from src.app.base import base

class User(base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    info: Mapped[str] = mapped_column(String(settings.MAX_LEN_INFO))
    otp_enable: Mapped[bool] = mapped_column()
    date_creation: Mapped[int] = mapped_column()
    
class UserModel:
    id = "id"
    username = "username"
    name = "name"
    email = "email"
    password = "password"
    info = "info"
    otp_enable = "otp_enable"
    date_creation = "date_creation"