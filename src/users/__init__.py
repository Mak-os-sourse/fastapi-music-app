from src.db import engine
from src.base import Base

from src.users.models import User
from src.users.routers import router

Base.metadata.create_all(engine)