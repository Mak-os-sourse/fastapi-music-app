import jwt
from fastapi import *

from src.users.crud import *
from src.config import secret_key

def auth_user(access: str = Query()) -> object | None:
    try:
        data_access = jwt.decode(access, secret_key, algorithms="HS256")
        
        user = get_user(username=data_access["username"])

        if user is not None:
            if user.username == data_access["username"] and data_access["password"] == user.password:
                return user
            else:
                return None
        else:
            raise HTTPException(401)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(400)