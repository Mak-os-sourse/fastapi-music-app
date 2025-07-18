import bcrypt
from fastapi import *
from fastapi.responses import *

from src.config import secret_key

from src.users.service import *
from src.users.dependencies import *
from src.users.crud import *

router = APIRouter()
tags_router = ["api-user"]

@router.get("/api/user/update-tokens", tags=tags_router)
async def update_tokens(response: Response, refresh: str = Cookie()):
        data_refresh = decode_token(token=refresh, secret_key=secret_key)

        if data_refresh is not None:
            tokens = create_tokens(username=data_refresh["username"], password=data_refresh["password"], secret_key=secret_key)
            response.set_cookie("refresh", tokens["refresh"], httponly=True)
            return tokens
        else:
            response.delete_cookie("refresh")
            raise HTTPException(401, "Error refresh token")

@router.post("/api/user/login", tags=tags_router)
async def login(response: Response, user_data: UserDataLogin = Body()):
    user = get_user(username=user_data.username)

    if user is not None:
        if bcrypt.checkpw(user_data.password.encode(), user.password.encode()) and user_data.username == user.username:
            tokens = create_tokens(username=user.username, password=user.password,
                                   secret_key=secret_key)
            response.set_cookie("refresh", tokens["refresh"], httponly=True)
            return tokens
        else:
            raise HTTPException(409, "Incorrect data")
    else:
        raise HTTPException(401, "unauthorized")


@router.post("/api/user/regist", tags=tags_router)
async def regist(response: Response, user_data: UserDataRegist = Body()):
    user_data.password = hash_pw(user_data.password)
    
    if get_user(username=user_data.username) is not None:
        raise HTTPException(409, "The use already exists")
    
    add_user(user_data)

    tokens = create_tokens(username=user_data.username, password=user_data.password,
                           secret_key=secret_key)
    response.set_cookie("refresh", tokens["refresh"], httponly=True)
    return tokens

@router.post("/api/user/logout", tags=tags_router)
async def logout(response: Response):
    response.delete_cookie("refresh")
    return RedirectResponse("/", status_code=200)

@router.delete("/api/user/delete", tags=tags_router)
async def delete_account(response: Response, user_data: UserDataLogin):
    delete_user(user_data)
    response.delete_cookie("refresh")