import asyncio
from fastapi import APIRouter, HTTPException, Depends, status, Body, Cookie, Response
from sqlalchemy import or_

from src.app.schemas.user import UserDataRegist, UserDataLogin, GenCode, VerifyCode, UpdatePassword
from src.app.service.security import hash_pw, create_tokens, decode_token
from src.app.service.otp import gen_otp, verifi_otp
from src.app.caching.decorators import cache_func
from src.app.depends.auth import auth_user
from src.app.service.email import email
from src.app.crud.user import user_crud
from src.app.models.user import User
from src.app.config import settings
from src.app.db import db

router = APIRouter(tags=["user"], prefix=settings.PREFIX_USER_API)

@router.post("/token/update/")
async def update_token(response: Response, access: str = Body(), token: str = Cookie()):
    access_data = decode_token(access, verify_exp=False)
    refresh_data = decode_token(token)
    if access_data is not None and refresh_data is not None:
        if access_data.get("username") == refresh_data.get("username") and access_data.get("password") == refresh_data.get("password"):
            access, refresh = create_tokens(refresh_data["username"], refresh_data["password"])
            response.set_cookie(settings.KEY_REFRESH_COOKIE, refresh)
            return {"access": access}
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

@router.post("/regist/")
async def regist(user_data: UserDataRegist = Body(), session = Depends(db.get_session)):
    users = await user_crud.crud.get_data(session, where=[or_(User.username == user_data.username, User.email == user_data.email)])
    
    if len(users) == 0:
        result = await user_crud.add(session, user_data.username, user_data.name, user_data.email, user_data.password)
        await cache_func.delete(namespace=settings.NAMESPACE_USER, match=f"*id:{result["id"]}*")
        return settings.STATUS_OK
    else:
        raise HTTPException(status.HTTP_409_CONFLICT)
    
@router.post("/login/")
async def login(response: Response, user_data: UserDataLogin = Body(), session = Depends(db.get_session)):
    user = await user_crud.get(session, **user_data.field, password=hash_pw(user_data.password))
    
    if len(user) == 1:
        user = user[0]
        if user["otp_enable"]:
            return {"email": user["email"]}
        else:
            access, refresh = create_tokens(user["username"], user["password"])
            response.set_cookie(settings.KEY_REFRESH_COOKIE, refresh, httponly=True)
            response.status_code = status.HTTP_201_CREATED
            return {"access": access}
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

@router.post("/code/generate/")
async def generate_code(data: GenCode = Body()):
    code, base32 = gen_otp()
    
    asyncio.create_task(email.send_mail(data.email, code))
    
    return {"life": settings.LIFE_OTP_CODE, "base32": base32}

@router.post("/login/code/verify/")
async def login_verify_code(response: Response, data: VerifyCode = Body(), session = Depends(db.get_session)):
    if verifi_otp(data.code, data.base32):
        user = await user_crud.get(session, **data.field, password=hash_pw(data.password))
        if len(user) == 1:
            user = user[0]
            access, refresh = create_tokens(user["username"], user["password"])
            response.set_cookie(settings.KEY_REFRESH_COOKIE, refresh, httponly=True)
            return {"access": access}
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

@router.post("/code/enable/")
async def enable_code(access = Depends(auth_user), session = Depends(db.get_session)):
    await user_crud.update(session, id=access["id"], otp_enable=True)
    return settings.STATUS_OK

@router.post("/code/disable/")
async def disable_code(access = Depends(auth_user), session = Depends(db.get_session)):
    await user_crud.update(session, id=access["id"], otp_enable=False)
    return settings.STATUS_OK

@router.put("/password/update/")
async def update_password(data: GenCode = Body(), session = Depends(db.get_session)):
    user = await user_crud.get(session, email=data.email)
        
    if user != []:
        return settings.STATUS_OK
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

@router.put("/password/update/code/verify/")
async def update_password_verify_code(data: UpdatePassword = Body(), session = Depends(db.get_session)):
    if verifi_otp(data.code, data.base32):
        user = await user_crud.get(session, email=data.email)
        if len(user) == 1:
            user = user[0]
            await user_crud.update(session, id=user["id"], password=hash_pw(data.new_password))
            await cache_func.delete(namespace=settings.NAMESPACE_USER, match=f"*id:{user["id"]}*")
            return settings.STATUS_OK
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

@router.delete("/delete/")
async def delete(response: Response, access = Depends(auth_user), session = Depends(db.get_session)):
    await user_crud.delete(session, id=access["id"])
    await cache_func.delete(namespace=settings.NAMESPACE_USER, match=f"*id:{access["id"]}*")
    response.delete_cookie(settings.KEY_REFRESH_COOKIE)
    return settings.STATUS_OK

@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie(settings.KEY_REFRESH_COOKIE)
    return settings.STATUS_OK