from sqlalchemy import select

from src.app.tests.utils.base import base_utils
from src.app.tests.models import Base
from src.app.tests.db import metadata, session
from src.app.tests.fake import fake
from src.app.crud.base import CRUD

crud = CRUD(Base)

async def test_add_data(session):
    username, password = fake.user_name(), fake.password()
    
    result = await crud.add_data(session, username=username, password=password)

    assert result["username"] == username and result["password"] == password
    
async def test_get_one_data(session):
    user = (await base_utils.add(session))[0]
    
    result = await crud.get_data(session, where=[Base.username == user["username"]])
    result = result[0]

    assert result["username"] == user["username"] and result["password"] == user["password"]
        
async def test_get_data_by_sorting(session):
    users = (await base_utils.add(session, 4))

    result = await crud.get_data(session, where=[Base.id.in_([i["id"] for i in users])],
                                 sorting=[(Base.username, False)])
    
    assert result == sorted(result, key=lambda x: x["username"], reverse=False)

async def test_update_data(session):
    user = (await base_utils.add(session))[0]
    new_username = fake.user_name()
    
    await crud.update_data(session, where=[Base.id == user["id"]], username=new_username)
    
    result = await session.scalars(select(Base).where(Base.id == user["id"]))
    result = result.one().__dict__
    
    assert result["username"] == new_username

async def test_delete_data(session):
    user = (await base_utils.add(session))[0]
    
    await crud.delete_data(session, id=1)

    new_data = await session.execute(select(Base))

    assert user != new_data