import pytest_asyncio
from fastapi.testclient import TestClient

from src.app.tests.db import db_test

from src.app.app import app
from src.app.db import db

@pytest_asyncio.fixture()
async def client():
    app.dependency_overrides[db.get_session] = db_test.get_session
    
    with TestClient(app) as client:
        yield client