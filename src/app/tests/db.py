import pytest_asyncio
from sqlalchemy import delete

from src.app.tests.models import *
from src.app.tests.config import settings_test

from src.app.base import base
from src.app.db import DataBase

db_test = DataBase(settings_test.DB_URL, False)

@pytest_asyncio.fixture(scope="session")
async def metadata():
    await db_test.metadata_drop_all(base)
    await db_test.metadata_create_all(base)
    session = db_test.Session()
    
    yield session
    
    await session.close()
    await db_test.metadata_drop_all(base)
    
@pytest_asyncio.fixture()
async def session(metadata):
    session = metadata
    
    yield session

    for value in base.metadata.tables.values():
        await session.execute(delete(value))
    await session.commit()
