from fastapi import *
from fastapi.encoders import jsonable_encoder

from src.db import session_db
from src.music.crud import get_music
from src.user_data.crud import add_activity, get_activity, delete_activity
from src.users.dependencies import auth_user
from src.user_data.models import *

router = APIRouter(tags=["user-data"])

@router.post("/api/user_data/{table}/add-interactions/")
async def router_add_activity(table: str = Path(), music_id: int = Query(), user = Depends(auth_user)):
    music = jsonable_encoder(get_music(session_db, where=[f"id == {music_id}"]))

    if music != []:
        if table == "Likes":
            add_activity(session_db, Likes, music_id=music_id, user_id=user.id)
        elif table == "Listening":
            add_activity(session_db, Listening, music_id=music_id, user_id=user.id)
        else:
            raise HTTPException(404, detail="Page not found")
    else:
        raise HTTPException(400, detail="Error, this music does not exist")

    return music[0]

@router.get("/api/user_data/{table}/get-interactions/")
async def router_get_activity(table: str = Path(), where: list = Query(), user = Depends(auth_user)):
    if table == "Likes":
        result = jsonable_encoder(get_activity(session_db, Likes, fields=where))
    elif table == "Subscribers":
        result = jsonable_encoder(get_activity(session_db, Subscribers, fields=where))
    else:
        raise HTTPException(404, detail="Page not found")

    list_where = []
    for i in result:
        list_where.append(f"id == {i["music_id"]}")

    return get_music(session_db, where=list_where)

@router.delete("/api/user_data/{table}/delete-interactions/")
async def router_delete_activity(table: str = Path(), music_id: int = Query(), user = Depends(auth_user)):
    if table == "Likes":
        table = Likes
    if table == "Listening":
        table = Listening

    result = delete_activity(session_db, Likes, user_id=user.id, music_id=music_id)
    return result

@router.delete("/api/user_data/{table}/delete-all-interactions/")
async def router_delete_activity(table: str = Path(), user = Depends(auth_user)):
    if user is not None:
        if table == "Likes":
            table = Likes
        if table == "Listening":
            table = Listening

        result = delete_activity(session_db, table, user_id=user.id)
        return result
    else:
        raise HTTPException(401, detail="interactions")