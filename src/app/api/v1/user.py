import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, status, File, Path, Depends, Query, Body
from fastapi.responses import FileResponse

from src.app.schemas.user import UserDataSearch, UserDataUpdate, UserResponseModel
from src.app.caching.decorators import cache_func, CacheConfig
from src.app.api.v1.endpoints.user import UserAPI
from src.app.service.storage import storage
from src.app.depends.auth import auth_user
from src.app.crud.user import user_crud
from src.app.config import settings
from src.app.db import db

router = APIRouter(tags=["user"])

@router.get(UserAPI.GET, response_model=UserResponseModel | None)
@cache_func.async_cache(namespace=settings.NAMESPACE_USER, exp=settings.EXP_USER_CACHE, update_time=True)
async def get_user(cache_config: CacheConfig = Depends(CacheConfig),
                   id: int = Path(), session = Depends(db.get_session)):
    cache_config.key = f"user:id:{id}"
    result = await user_crud.get(session, id=id)
    return result[0] if result else None

@router.get(UserAPI.ME, response_model=UserResponseModel | None)
@cache_func.async_cache(namespace=settings.NAMESPACE_USER, exp=settings.EXP_USER_CACHE, update_time=True)
async def get_me(cache_config: CacheConfig = Depends(CacheConfig),
                   access = Depends(auth_user),
                   session = Depends(db.get_session)):
    cache_config.key = f"user:id:{access['id']}"
    result = await user_crud.get(session, id=access["id"])
    return result[0] if result else None

@router.get(UserAPI.SEARCH, response_model=list[UserResponseModel] | None)
@cache_func.async_cache(exp=settings.EXP_USER_CACHE, namespace=settings.NAMESPACE_USER)
async def search_user(cache_config: CacheConfig = Depends(CacheConfig),
                      data: UserDataSearch = Query(),
                      session = Depends(db.get_session)):
    args = data.model_dump()
    user_data = args["field"] if args["field"] is not None else {}
    args.pop("field")
    
    result = await user_crud.search(session, **args, **user_data)
    list_id = [f'id:{element.copy().pop("id")}' for element in result.copy()]
    cache_config.key = f"user:{list_id}"

    return result

@router.put(UserAPI.UPDATE)
async def update_user(data: UserDataUpdate = Body(), access = Depends(auth_user), session = Depends(db.get_session)):
    await cache_func.delete(namespace=settings.NAMESPACE_USER, match=f"*id:{access["id"]}*")
    await user_crud.update(session, id=access["id"], **data.field)
    return settings.STATUS_OK

@router.post(UserAPI.SET_IMAGE)
async def set_image(image: UploadFile = File(), access = Depends(auth_user)):
    format_file = image.filename.split(".", -1)[-1]

    if format_file.lower() in settings.FORMAT_IMAGE:
        path = settings.PATH_USER_IMAGE / f"{access["id"]}.{settings.BASE_FORMAT_IMAGE}"
                
        asyncio.create_task(storage.convert(await image.read(), path, vf=f"scale={settings.SCALE_IAMGE}:{settings.SCALE_IAMGE}"))
        await cache_func.delete(namespace=settings.NAMESPACE_USER, match=f"*user-image:id:{access["id"]}*")
        return settings.STATUS_OK
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    
@router.get(UserAPI.GET_IMAGE)
@cache_func.async_cache(namespace=settings.NAMESPACE_USER, exp=settings.EXP_USER_CACHE, update_time=True)
async def get_image(cache_config: CacheConfig = Depends(CacheConfig), id: str = Path()):
    cache_config.key = f"user-image:id:{id}"
    path = settings.PATH_USER_IMAGE / f"{id}.{settings.BASE_FORMAT_IMAGE}"

    if storage.exists_path(path):
        return FileResponse(path)
    else:
        return None