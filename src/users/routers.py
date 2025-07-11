import bcrypt
from fastapi.responses import *

from src.config import secret_key
from src.users.dependencies import *
from src.users.schemas import *
from src.users.crud import *

router = APIRouter()
tags_router = ["api-user"]

@router.get("/api/user/update-tokens", tags=tags_router)
async def update_tokens(response: Response, refresh: str = Cookie()):
    try:
        data_refresh = jwt.decode(refresh, secret_key, algorithms="HS256")

        return create_tokens(response, UserDataLogin(username=data_refresh["username"], password=data_refresh["password"]))
    except:
        response.delete_cookie("refresh")
        return HTTPException(401, "Error refresh token")

@router.post("/api/user/login", tags=tags_router)
async def login(response: Response, user_data: UserDataLogin = Body()):
    user = get_user(username=user_data.username)

    if user is not None:
        if bcrypt.checkpw(user_data.password.encode(), user.password.encode()) and user_data.username == user.username:
            return create_tokens(response, user)
        else:
            return HTTPException(409, "Incorrect data")
    else:
        return HTTPException(401, "unauthorized")


@router.post("/api/user/regist", tags=tags_router)
async def regist(response: Response, user_data: UserDataRegist = Body()):
    user_data.password = hash_pw(user_data.password)
    
    if get_user(username=user_data.username) is not None:
        return HTTPException(409, "The use already exists")
    
    add_user(user_data)
    return create_tokens(response, user_data)

@router.post("/api/user/logout", tags=tags_router)
async def logout(response: Response):
    response.delete_cookie("refresh")
    return RedirectResponse("/", status_code=200)

@router.delete("/api/user/delete", tags=tags_router)
async def delete_account(response: Response, user_data: UserDataLogin):
    delete_user(user_data)
    response.delete_cookie("refresh")