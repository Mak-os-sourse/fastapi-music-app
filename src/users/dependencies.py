import jwt, uuid, bcrypt
from fastapi import *
from fastapi.responses import *
from datetime import datetime, timezone, timedelta

from src.users.crud import *
from src.users.schemas import *
from src.config import secret_key

def hash_pw(password: str) -> str:
    hash_str = str(bcrypt.hashpw(password.encode(), bcrypt.gensalt()))
    hash_str = hash_str.replace("b", "", 1).replace("'", "", -1)
    return hash_str

def create_tokens(response: Response, user_data: UserDataLogin) -> dict:
    refresh = jwt.encode({"jti": str(uuid.uuid4()),
                                "exp": datetime.now(timezone.utc) + timedelta(days=30),
                                "username": user_data.username,
                                "password": user_data.password},
                                secret_key, algorithm="HS256")
    access =  jwt.encode({"jti": str(uuid.uuid4()),
                                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
                                "username": user_data.username,
                                "password": user_data.password},
                                secret_key, algorithm="HS256")
    
    response.set_cookie("refresh", refresh, httponly=True)
    return {"access": access, "refresh": refresh}

def auth_user(access: str = Query()) -> object | None:
    try:
        data_access = jwt.decode(access, secret_key, algorithms="HS256")
        
        user = get_user(username=data_access["username"])
        print(data_access["password"], user.password)
        if user is not None:
            if user.username == data_access["username"] and data_access["password"] == user.password:
                return user
            else:
                return None
        else:
            return None
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return None