from src.base import Base
from src.db import engine

from src.user_data.models import Likes, Favorites, Listening
from src.user_data.routers import router

Base.metadata.create_all(engine)