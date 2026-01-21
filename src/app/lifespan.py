from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.app.db import db
from src.app.base import base
from src.app.cache import rc

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.metadata_create_all(base)
    yield
    await rc.aclose()
    await db.engine.dispose()