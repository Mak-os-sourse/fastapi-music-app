from src.db import engine
from src.base import Base
from src.music.models import Music
from src.music.routers import router

Base.metadata.create_all(engine)