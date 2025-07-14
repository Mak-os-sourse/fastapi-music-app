from fastapi import *

from src.db import session_db
from src.user_data.crud import add_activity, get_activity, delete_activity
from src.users.dependencies import auth_user

router = APIRouter(tags=["user-data"])

@router.post("/api/user_data/{table}/add-activity/")
async def router_add_activity(table: Path(), music_id: int = Query(), user = Depends(auth_user)):
    if user is not None:
        result = add_activity(session_db, table, music_id=music_id, user_id=user.id)
        return result
    else:
        raise HTTPException(401, detail="Unauthorized")

@router.get("/api/user_data/{table}/get-activity/")
async def router_get_activity(table: Path(), user = Depends(auth_user)):
    if user is not None:
        result = get_activity(session_db, table, user.id)
        return result
    else:
        raise HTTPException(401, detail="Unauthorized")

@router.delete("/api/user_data/{table}/delete-activity/")
async def router_delete_activity(table: Path(), music_id: int = Query(), user = Depends(auth_user)):
    if user is not None:
        result = delete_activity(session_db, table, user_id=user.id, music_id=music_id)
        return result
    else:
        raise HTTPException(401, detail="Unauthorized")