import jwt

from fastapi import HTTPException

from src.app.tests.config import settings_test
from src.app.tests.utils.user import user_utils
from src.app.tests.cache import close_pool
from src.app.tests.db import metadata, session
from src.app.tests.fake import fake

from src.app.depends.auth import auth_user
from src.app.config import settings

async def test_auth(close_pool, session):
    user = (await user_utils.add(session))[0]
    
    token = jwt.encode({"username": user["username"],
                        "password": user["password"]},
                       settings.SECRET_KEY,
                       algorithm="HS256")
    
    result = await auth_user(response = settings_test.RESPONSE, access=token, session=session)

    for key, value in result.items():
        assert value == user[key]

async def test_bad_token_auth(close_pool, session):
    try:
        await auth_user(response = settings_test.RESPONSE, access="", session=session)
    except HTTPException as e:
        assert e.status_code == 403

async def test_fail_user_auth(close_pool, session):
    user = (await user_utils.add(session))[0]
    
    token = jwt.encode({"username": user["username"],
                        "password": fake.password()},
                       settings.SECRET_KEY,
                       algorithm="HS256")
    
    try:
        await auth_user(response = settings_test.RESPONSE, access=token, session=session)
    except HTTPException as e:
        assert e.status_code == 401