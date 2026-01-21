import asyncio
import sox
from fastapi import APIRouter, UploadFile, HTTPException, status, File, Depends, Path, Query, Body
from fastapi.responses import Response, FileResponse

from src.app.caching.decorators import cache_func
from src.app.service.storage import storage
from src.app.depends.auth import auth_user
from src.app.schemas.music import SetMusic, SearchMusic, UpdateMusicData
from src.app.crud.music import music_crud
from src.app.config import settings
from src.app.db import db

router = APIRouter(tags=["music"], prefix=settings.PREFIX_MUSIC_API)

@router.get("/genres/get/")
@cache_func.async_cache(exp=3600, update_time=True)
async def get_genres():
    return settings.MUSIC_GENRES

@router.post("/add/music/")
async def add_music(data: SetMusic = Body(),
                    access = Depends(auth_user),
                    session = Depends(db.get_session)):
    music_data = await music_crud.get(session, name=data.name, artists=[access["id"]])

    if music_data:
        if data.genre.lower() in settings.MUSIC_GENRES:
            await music_crud.add(session, name=data.name, genre=data.genre, artists=[access["id"]],
                                 info=data.info, text=data.text, size_file=0, duration_sec=0, is_private=data.is_private)
            
            return settings.STATUS_OK
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

@router.get("/get/{id}/")    
async def get_music(id: int = Path(), session = Depends(db.get_session)):
    result = await music_crud.get(session, id=id, is_private=False)
    result = await music_crud.load_depends(session, result)
    return result[0] if result else None

@router.get("/search/")
async def search_music(data: SearchMusic = Query(), session = Depends(db.get_session)):
    args = data.model_dump()
    music_data = args["field"] if args["field"] is not None else None
    args.pop("field")
    
    result = await music_crud.search(session, **args, **music_data, is_private=False)
    return await music_crud.load_depends(session, result)
    
@router.get("/get/audio/{id}/")
async def get_audio(id: int = Path(),
                    start: int = Query(default=0),
                    end: int = Query(default=-1)):
    path = settings.PATH_USER_MUSIC / f"{id}.{settings.BASE_FORMAT_MUSIC}"
    
    if storage.exists_path(path):
        size_file = (storage.path / path).stat().st_size
        
        data = await storage.read_file(path, seek=start, size=abs(end - start))
            
        headers = {"size-file": str(size_file)}
        
        return Response(data, headers=headers, media_type="audio/mpeg")
    else:
        return None

@router.get("/get/cover/{id}/")
async def get_cover(id: int = Path()):
    path = settings.PATH_MUSIC_COVER / f"{id}.{settings.BASE_FORMAT_IMAGE}"
    
    if storage.exists_path(path):
        return FileResponse(storage.path / path, media_type="image/png")
    else:
        return None
    
@router.put("/update/data/")
async def update_music_data(id: int = Query(),
                            data: UpdateMusicData = Body(),
                            access = Depends(auth_user),
                            session = Depends(db.get_session)):
    await music_crud.update(session, id=id, artist_id=access["id"], **data.field)
    return settings.STATUS_OK

@router.put("/set/files/")
async def update_music_file(id: int = Query(),
                            music: UploadFile = File(default=None),
                            cover: UploadFile = File(default=None),
                            access = Depends(auth_user),
                            session = Depends(db.get_session)):
    music_data = await music_crud.get(session, id=id, artists=access["id"])
    
    if music_data:
        music_data = music_data[0]
        
        if music is not None:
            path =  settings.PATH_USER_MUSIC / f"{music_data["id"]}.{settings.BASE_FORMAT_MUSIC}"
            format_music = music.filename.split(".", -1)[-1]
            
            if format_music.lower() in settings.FORMAT_MUSIC:
                music_bytes = await music.read()
                size_file = len(music_bytes)
                
                await storage.write_file(path, music_bytes)

                length = sox.file_info.duration(storage.path / path)
                
                if length / 60 > settings.LENGTH_MUSIC:
                    await storage.delete_file(path)
                    raise HTTPException(status.HTTP_400_BAD_REQUEST)
                
                asyncio.create_task(storage.convert(music_bytes, path))
                await music_crud.update(session, id=music_data["id"], artist_id=access["id"], size_file=size_file)
            else:
                raise HTTPException(status.HTTP_400_BAD_REQUEST)
        if cover is not None:
            format_image = cover.filename.split(".", -1)[-1]
            
            if format_image.lower() in settings.FORMAT_IMAGE:
                asyncio.create_task(storage.convert(await cover.read(), settings.PATH_MUSIC_COVER / f"{music_data["id"]}.{settings.BASE_FORMAT_IMAGE}", 
                                                    vf=f"scale={settings.SCALE_IAMGE}:{settings.SCALE_IAMGE}"))
            else:
                raise HTTPException(status.HTTP_400_BAD_REQUEST)
        return settings.STATUS_OK
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    
@router.delete("/delete/")
async def delete_music(id: int = Query(),
                       access = Depends(auth_user),
                       session = Depends(db.get_session)):
    await music_crud.delete(session, id, artist_id=access["id"])
    try:
        await storage.delete_file(settings.PATH_USER_MUSIC / f"{id}.{settings.BASE_FORMAT_MUSIC}")
        await storage.delete_file(settings.PATH_MUSIC_COVER / f"{id}.{settings.BASE_FORMAT_IMAGE}")
        return settings.STATUS_OK
    except OSError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)