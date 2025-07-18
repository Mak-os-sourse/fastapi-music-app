import os
from fastapi import *
from fastapi.responses import FileResponse

from src.db import session_db
from src.music.crud import *
from src.music.schemas import MusicDataCreate, MusicDataGet, MusicDataChange
from src.users.dependencies import auth_user

router = APIRouter(tags=["api-music"])

@router.post("/api/music/add-music/")
async def router_create_music(upload_file: UploadFile = File(), music_data_create: MusicDataCreate = Query(), user = Depends(auth_user)):
    if user is not None:

        music = add_music(session_db, user_id=user.id, title=music_data_create.title, genre=music_data_create.genre, info=music_data_create.info)

        with open(f"static/api/music/{music.id}.mp3", "wb") as file:
            file.write(await upload_file.read())
        return music
    else:
        return HTTPException(401, "Unauthorized")

@router.get("/api/music/get-music/")
def router_get_musics(music_data_get: MusicDataGet = Query(default=None)):
    sorting = []

    for i in music_data_get.sorting:
        field = i.split(":")[0]
        reverse = i.split(":")[1]

        if reverse.lower() == "true":
            sorting.append((field, True))
        if reverse.lower() == "false":
            sorting.append((field, False))

    return get_music(session_db, limit=music_data_get.limit, offset=music_data_get.offset, sorting=sorting, where=music_data_get.where)

@router.get("/api/music/download-music/", response_class=FileResponse)
def router_download_music(id: int):
    return FileResponse(f"static/api/music/{id}.mp3")

@router.put("/api/music/change-user-music")
async def router_change_user_music(upload_file: UploadFile = File(default=None), music_data_change: MusicDataChange = Query(), user = Depends(auth_user)):
    change_user_music(session_db, id=music_data_change.id, title=music_data_change.title, genre=music_data_change.genre, info=music_data_change.info)

    if upload_file is not None:
        with open(f"static/api/music/{music_data_change.id}.mp3", "wb") as file:
            file.write(await upload_file.read())

@router.delete("/api/music/delete-user-music")
async def router_delete_user_music(id: int = Query(), user = Depends(auth_user)):
    delete_user_music(session_db, id, user.id)

    os.remove(f"static/api/music/{id}.mp3")