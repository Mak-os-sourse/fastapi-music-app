import hashlib
import jwt
from datetime import datetime, timedelta, timezone

from src.app.tests.fake import fake

from src.app.service.security import hash_pw, create_tokens, decode_token
from src.app.config import settings

async def test_hash_password():
    password = fake.password()
    
    result = hash_pw(password)
    
    assert hashlib.sha256(f"{password + settings.SALT}".encode()).hexdigest() == result
    
async def test_create_token():
    username, password = fake.user_name(), fake.password()
    
    access, refresh = create_tokens(username, password)
    access = jwt.decode(access, settings.SECRET_KEY, algorithms="HS256")
    refresh = jwt.decode(refresh, settings.SECRET_KEY, algorithms="HS256")
        
    assert access["username"] == username and refresh["username"] == username
    assert access["password"] == password and refresh["password"] == password
    assert datetime.fromtimestamp(refresh["exp"]).date() == (datetime.now(timezone.utc) + timedelta(days=settings.EXP_DAYS_REFRESH)).date()
    assert datetime.fromtimestamp(access["exp"]).date() == (datetime.now(timezone.utc) + timedelta(minutes=settings.EXP_MINUTES_ACCESS)).date()
    
async def test_decode_token():
    token = jwt.encode({"username": fake.user_name(), "password": fake.password()}, settings.SECRET_KEY, algorithm="HS256")
    
    result = decode_token(token)
    
    assert jwt.decode(token, settings.SECRET_KEY, algorithms="HS256") == result

async def test_ignor_exp_decode_token():
    token = jwt.encode({"exp": datetime.now(timezone.utc).timestamp() - 122,"username": fake.user_name(), "password": fake.password()}, settings.SECRET_KEY, algorithm="HS256")
    
    result = decode_token(token, verify_exp=False)
    
    assert jwt.decode(token, settings.SECRET_KEY, algorithms="HS256", options={"verify_exp": False}) == result

async def test_fail_decode_token():
    assert decode_token("") is None