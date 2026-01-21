import pyotp
import jwt
import hashlib
from sqlalchemy import select
from unittest.mock import patch

from src.app.depends.auth import auth_user
from src.app.service.email import email
from src.app.models.user import User
from src.app.config import settings
from src.app.app import app

from src.app.tests.utils.user import add_users
from src.app.tests.config import settings_test
from src.app.tests.client import client
from src.app.tests.cache import cache
from src.app.tests.db import session
from src.app.tests.fake import fake

async def test_update_token(client):
    username, password = fake.user_name(), fake.password()
    refresh = jwt.encode({"username": username, "password": password}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    access = jwt.encode({"exp": 0, "username": username, "password": password}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
                        
    result = client.post(f"{settings_test.USER_PATH}/token/update/", json=access, cookies={settings.KEY_REFRESH_COOKIE: refresh})

    access = jwt.decode(result.json()["access"], settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    
    assert result.status_code == 200
    assert access["username"] == username
    assert access["password"] == password
    assert client.cookies.get(settings.KEY_REFRESH_COOKIE)

async def test_fail_update_token(client):
    result = client.post(f"{settings_test.USER_PATH}/token/update/", json="", cookies={settings.KEY_REFRESH_COOKIE: ""})

    assert result.status_code == 400

async def test_fake_access_update_token(client):
    username, password = fake.user_name(), fake.password()
    refres = jwt.encode({"username": username, "password": password}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    access = jwt.encode({"exp": 0}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    result = client.post(f"{settings_test.USER_PATH}/token/update/", json=access, cookies={settings.KEY_REFRESH_COOKIE: refres})
    
    assert result.status_code == 403

async def test_regist(cache, session, client):
    name, username, email, password = fake.user_name(), fake.user_name(), fake.email(), fake.password()
    
    result = client.post("api/v1/user/regist/", json={"name": name, "username": username, "email": email, "password": password})
    
    stmt = await session.scalars(select(User).where(User.username == username))
    user = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert len(await cache.rc.keys()) == 0
    assert user.username == username
    assert user.name == name
    assert user.email == email
    assert user.password != password
        
async def test_fail_email_regist(session, client):
    user = (await add_users(session, retrun_hash_pw=False))[0]
    
    result = client.post("api/v1/user/regist/", json={"name": user["name"], "username": user["username"],
                                                      "email": user["email"], "password": user["password"]})
    
    assert result.status_code == 409
    
async def test_login_otp_enable(session, client):
    user = (await add_users(session, retrun_hash_pw=False))[0]
    
    result = client.post("api/v1/user/login/", json={"field": user["email"], "password": user["password"]})

    assert result.status_code == 200
    assert result.json() == {"email": user["email"]}
    
async def test_login_otp_disable(session, client):
    user = (await add_users(session, otp_enable=False, retrun_hash_pw=False))[0]
    
    result = client.post("api/v1/user/login/", json={"field": user["email"], "password": user["password"]})

    token = jwt.decode(result.json()['access'], settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert result.status_code == 201
    assert token["username"] == user["username"]
    assert token["password"] == hashlib.sha256(f"{user["password"]}{settings.SALT}".encode()).hexdigest()
    assert client.cookies.get(settings.KEY_REFRESH_COOKIE) is not None
    
async def test_fail_login(session, client):
    result = client.post("api/v1/user/login/", json={"field": fake.email(), "password": fake.password()})
    
    assert result.status_code == 401

@patch(f"{email.send_mail.__module__}.email.{email.send_mail.__name__}")  
async def test_gen_code(mock, client):
    mock.return_value = None
    
    result = client.post(f"{settings_test.USER_PATH}/code/generate/", json={"email": fake.email()})
    data = result.json()
    assert result.status_code == 200
    assert data.get("life") is not None
    assert data.get("base32") is not None
    
async def test_login_verify_code(session, client):
    totp = pyotp.TOTP(settings_test.BASE32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    code = totp.now()
    
    user = (await add_users(session, retrun_hash_pw=False))[0]
    
    result = client.post(f"{settings_test.USER_PATH}/login/code/verify/", json={"code": code, "field": user["email"],
                                                                  "password": user["password"], "base32": settings_test.BASE32})

    token = jwt.decode(result.json()['access'], settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    
    assert result.status_code == 200
    assert token["username"] == user["username"]
    assert token["password"] == hashlib.sha256(f"{user["password"]}{settings.SALT}".encode()).hexdigest()
    assert client.cookies.get(settings.KEY_REFRESH_COOKIE) is not None

async def test_fail_code_login_verify(session, client):
    user = (await add_users(session, retrun_hash_pw=False))[0]
    
    result = client.post(f"{settings_test.USER_PATH}/login/code/verify/", json={"code": "", "field": user["email"],
                                                                  "password": user["password"], "base32": settings_test.BASE32})

    assert result.status_code == 400

async def test_fail_data_login_verify(session, client):
    totp = pyotp.TOTP(settings_test.BASE32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    code = totp.now()
    
    result = client.post(f"{settings_test.USER_PATH}/login/code/verify/", json={"code": code, "base32": settings_test.BASE32, "field": fake.email(), "password": fake.password()})

    assert result.status_code == 400
    
async def test_enable_code(session, client):
    user = (await add_users(session, otp_enable=False))[0]
    app.dependency_overrides[auth_user] = lambda: user

    result = client.post(f"{settings_test.USER_PATH}/code/enable/", json=user["id"])
    
    stmt = await session.scalars(select(User).where(User.id == user["id"]))
    update = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert update.otp_enable
    
async def test_disable_code(session, client):
    user = (await add_users(session, otp_enable=False))[0]
    app.dependency_overrides[auth_user] = lambda: user
    
    result = client.post(f"{settings_test.USER_PATH}/code/disable/", json=user["id"])
    
    stmt = await session.scalars(select(User).where(User.id == user["id"]))
    update = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert not update.otp_enable

async def test_update_password(session, client):
    user = (await add_users(session))[0]
    
    result = client.put(f"{settings_test.USER_PATH}/password/update/", json={"email": user["email"]})

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK

async def test_fail_update_password(session, client):
    result = client.put(f"{settings_test.USER_PATH}/password/update/", json={"email": fake.email()})

    assert result.status_code == 401

async def test_update_password_verify_code(cache, session, client):
    totp = pyotp.TOTP(settings_test.BASE32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    code = totp.now()

    new_password = fake.password()
    user = (await add_users(session, retrun_hash_pw=False))[0]
    
    result = client.put(f"{settings_test.USER_PATH}/password/update/code/verify/", json={"code": code, "email": user["email"],
                                                                "new_password": new_password, "base32": settings_test.BASE32})
    
    stmt = await session.scalars(select(User).where(User.id == user["id"]))
    update = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert len(await cache.rc.keys()) == 0
    assert update.password == hashlib.sha256(f"{new_password}{settings.SALT}".encode()).hexdigest()

async def test_fail_code_update_password_verify_code(client):
    result = client.put(f"{settings_test.USER_PATH}/password/update/code/verify/", json={"code": "", "email": fake.email(),
                                                                "new_password": fake.password(), "base32": pyotp.random_base32()})
    assert result.status_code == 400

async def test_no_user_update_password_verify_code(session, client):
    totp = pyotp.TOTP(settings_test.BASE32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    code = totp.now()
    
    result = client.put(f"{settings_test.USER_PATH}/password/update/code/verify/", json={"code": code, "base32": settings_test.BASE32, "email": fake.email(),
                                                                "new_password": fake.password()})
    assert result.status_code == 401
    
async def test_delete_user(cache, session, client):
    user = (await add_users(session))[0]
    app.dependency_overrides[auth_user] = lambda: user
    await cache.rc.set(f"{settings.PREFIX_CACHE_FUNC}-{settings.NAMESPACE_USER}: -user-image:id:{user["id"]}", "")
    
    result = client.delete(f"{settings_test.USER_PATH}/delete/")
    
    stmt = await session.scalars(select(User).where(User.id == user["id"]))
    data = stmt.one_or_none()
    
    assert data is None
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert len(await cache.rc.keys()) == 0
    assert client.cookies.get(settings.KEY_REFRESH_COOKIE) is None
     
async def test_logout_user(client):
    client.cookies.set(settings.KEY_REFRESH_COOKIE, "", domain="testserver.local")
    result = client.post(f"{settings_test.USER_PATH}/logout/")
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert client.cookies.get(settings.KEY_REFRESH_COOKIE) is None