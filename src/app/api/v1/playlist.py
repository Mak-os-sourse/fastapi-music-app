import json
from fastapi import APIRouter, HTTPException, status, Path, Body, Query, Depends

from src.app.schemas.playlist import AddUserData, CreateUserData, GetUserData, SearchUserData, SearchData, UpdateUserData
from src.app.crud.playlist import playlist_crud
from src.app.models.playlist import PlayList
from src.app.models.music import Music
from src.app.depends.auth import auth_user
from src.app.config import settings
from src.app.db import db

router = APIRouter(tags=["user_data"], prefix=settings.PREFIX_USER_DATA)

def check_table(table: str = Path()):
    data = {"like": "like", "repost": "repost", "album": "album", "playlist": "playlist", "views": "views"}
    
    if data.get(table.lower(), False):
        return data[table.lower()]
    else:
        raise HTTPException(status.HTTP_100_CONTINUE)

@router.post("/{table}/create/")
async def create_user_data(data: CreateUserData = Body(), model: str = Depends(check_table),
                       access = Depends(auth_user), session = Depends(db.get_session)):
    if model in ["album", "playlist"]:
        result = await playlist_crud.get(session, title=data.title, artist=access["id"], kind=model)
        
        if result == []:
            await playlist_crud.add(session, data.title, music=[], artist=access["id"], kind=model, is_private=data.is_private)
            return settings.STATUS_OK
        else:
            raise HTTPException(status.HTTP_409_CONFLICT)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

@router.post("/{table}/add/")
async def add_user_data(data: AddUserData = Body(), model: str = Depends(check_table),
                        access = Depends(auth_user), session = Depends(db.get_session)):
    result = await playlist_crud.get(session, artist=access["id"], kind=model)
    
    if result != []:
        result = result[0]
        new_music = result["music"]
        
        for item in data.music:
            if item not in new_music:
                new_music.append(item)
        
        if model == "album":
            await playlist_crud.crud.update_data(session, music=json.dumps(new_music),
                                                 where=[PlayList.id == result["id"], PlayList.artist == access["id"],
                                                        Music.artists.like(f"%{access["id"]}%")])
        else:
            await playlist_crud.update(session, id=result["id"], artist_id=result["artist"], music=new_music)
        return settings.STATUS_OK
    else:
        if model not in ["album", "playlist"]:
            await playlist_crud.add(session, title="", artist=access["id"],
                                    music=data.music,
                                    kind=model, is_private=False)
            return settings.STATUS_OK
        else:
            raise HTTPException(status.HTTP_409_CONFLICT)

@router.delete("/{table}/delete/music/")
async def delete_album_music(id: int = Query(),
                             music_id: int = Query(),
                             model: str = Depends(check_table),
                             access = Depends(auth_user),
                             session = Depends(db.get_session)):
    playlist = await playlist_crud.get(session, id=id, artist=access["id"], kind=model)

    if playlist:
        playlist = playlist[0]
        
        for value in playlist["music"]:
            if value == music_id:
                playlist["music"].remove(value)
        
        await playlist_crud.update(session, id=playlist["id"], artist_id=access["id"], music=playlist["music"])
        return settings.STATUS_OK
    else:
        raise HTTPException(status.HTTP_409_CONFLICT)

@router.get("/{table}/get/")
async def get_user_data(data: GetUserData = Query(),
                        model: str = Depends(check_table),
                        session = Depends(db.get_session)):
    args = data.model_dump()
    data = args.pop("field")
    
    result = await playlist_crud.get(session, **data, kind=model, is_private=False)
    result = await playlist_crud.load_depends(session, result, offset=args.get("offset", 0),
                                              limit=args.get("limit", 10), sorting=args["sorting"])
    
    return result

@router.get("/{table}/get/my/")
async def get_user_data(data: SearchData = Query(), model: str = Depends(check_table),
                        access = Depends(auth_user), session = Depends(db.get_session)):
    args = data.model_dump()
    
    result = await playlist_crud.get(session, artist=access["id"], kind=model)
    result = await playlist_crud.load_depends(session, result, offset=args.get("offset", 0),
                                              limit=args.get("limit", 10), sorting=args["sorting"])
    return result

@router.get("/{table}/search/")
async def search_album(data: SearchUserData = Query(),
                       model: str = Depends(check_table),
                       session = Depends(db.get_session)):
    args = data.model_dump()
    music_data = args["field"] if args["field"] is not None else None
    count_music = args.pop("count_music")
    args.pop("field")
    
    result = await playlist_crud.search(session, **args, **music_data, kind=model, is_private=False)
    return await playlist_crud.load_depends(session, result, limit=count_music)

@router.put("/{table}/update/data/")
async def update_album(id: int = Query(), data: UpdateUserData = Body(),
                       model: str = Depends(check_table), access = Depends(auth_user),
                       session = Depends(db.get_session)):
    if data.field.get("title") is not None and model not in ["album", "playlist"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    else:
        await playlist_crud.update(session, id, artist_id=access["id"], **data.field)
        return settings.STATUS_OK

@router.delete("/{table}/delete/")
async def delete_album(id: int = Query(), model: str = Depends(check_table),
                       access = Depends(auth_user), session = Depends(db.get_session)):
    await playlist_crud.delete(session, id, artist=access["id"], kind=model)
    return settings.STATUS_OK