from src.app.tests.fake import fake
from src.app.tests.db import metadata, session
from src.app.tests.utils.user import user_utils

from src.app.models.user import User, UserModel
from src.app.service.security import hash_pw
from src.app.crud.user import user_crud
from src.app.config import settings

async def test_add_user(session):
    username, name, email, password = fake.user_name(), fake.name(), fake.email(), fake.password()
    
    result = await user_crud.add(session, username=username, name=name, email=email, password=password)
    
    assert result[UserModel.username] == username.lower()
    assert result[UserModel.name] == name.lower()
    assert result[UserModel.email] == email.lower()
    assert result[UserModel.password]  == hash_pw(password)
    assert result[UserModel.info] == ""
    assert isinstance(result["date_creation"], int)

async def test_get_user(session):
    user = (await user_utils.add(session))[0]
    
    result = await user_crud.get(session, username=user[UserModel.username])
    result = result[0]
    
    assert result == user

async def test_search_user(session):
    user = (await user_utils.add(session, 6))[0]
    username = user[UserModel.username][:len(user[UserModel.username]) - 1]
    
    result = await user_crud.search(session, username=username)
    result = result[0]
    
    assert result == user
    
async def test_search_user_by_sorting(session):
    await user_utils.add(session, 6)
    
    result = await user_crud.search(session, sorting=[(User.id, True)])
    
    assert result == sorted(result, key=lambda x: x["id"], reverse=True)

async def test_update_user(session):
    user = (await user_utils.add(session))[0]
    new_info = fake.text()
    
    await user_crud.update(session, id=user[UserModel.id], info=new_info)
    
    result = await user_utils.get(session, id=user[UserModel.id])

    assert result[UserModel.info] == new_info

async def test_delete_user(session):
    user = (await user_utils.add(session))[0]
    
    await user_crud.delete(session, id=user[UserModel.id])
    
    result = await user_utils.get(session, id=user[UserModel.id])
    
    assert result is None