import jwt
from fastapi import Header, Depends, HTTPException, status

from src.app.caching.decorators import cache_func, CacheConfig
from src.app.crud.user import user_crud
from src.app.config import settings
from src.app.db import db

@cache_func.async_cache(exp=settings.EXP_USER_CACHE, namespace=settings.NAMESPACE_USER)
async def auth_user(cache_config: CacheConfig = Depends(CacheConfig), 
                    access: str = Header(),
                    session = Depends(db.get_session)) -> object | None:
    try:
        data_access = jwt.decode(access, settings.SECRET_KEY, algorithms="HS256")
        
        user = await user_crud.get(session, username=data_access["username"], password=data_access["password"])

        if user != []:
            user = user[0]
            cache_config.key = f"user:id:{user["id"]}"
            return user
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(status.HTTP_403_FORBIDDEN)