import jwt
import uuid
import hashlib
from datetime import datetime, timezone, timedelta

from src.app.config import settings

def hash_pw(password: str) -> str:
    return hashlib.sha256(f"{password + settings.SALT}".encode()).hexdigest()

def create_tokens(username: str, password: str) -> list[str]:
    refresh = jwt.encode({"jti": str(uuid.uuid4()),
                          "exp": datetime.now(timezone.utc) + timedelta(days=settings.EXP_DAYS_REFRESH),
                          "username": username,
                          "password": password},
                          settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    access = jwt.encode({"jti": str(uuid.uuid4()),
                         "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.EXP_MINUTES_ACCESS),
                         "username": username,
                         "password": password},
                         settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return access, refresh

def decode_token(token: str, verify_exp: bool = True) -> str | None:
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM, options={"verify_exp": verify_exp})

        return data
    except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return None