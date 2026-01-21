import json
from sqlalchemy import func
from datetime import datetime, timezone

from src.app.crud.base import CRUD
from src.app.models.music import Music
from src.app.models.playlist import PlayList
from src.app.models.user import User
from src.app.utils.user import del_security

class MusicCRUD:
    def __init__(self):
        # self.crud = CRUD(Music, func.count(PlayList).label("sum"))
        self.crud = CRUD(Music)
        self.user_crud = CRUD(User)
        
    async def add(self, session,
                  name: str, genre: str, artists: list[int],
                  size_file: str, duration_sec: int,
                  info: str = "", text: str = "", 
                  is_private: bool = True) -> dict:
        return await self.crud.add_data(session, name=name.lower(), genre=genre, info=info, text=text, artists=json.dumps(artists),
                                        size_file=size_file, duration_sec=duration_sec, is_private=is_private,
                                        date_creation=int(datetime.now(timezone.utc).timestamp()))
        
    async def get(self, session, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = self._create_where(fields)
        
        result = await self.crud.get_data(session, where=where, offset=offset, limit=limit)
        
        return self._loads_json(result)
    
    async def search(self, session, sorting: list[tuple[object, bool]] = None, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = []
        
        for key, value in fields.items():
            field = getattr(Music, key)
            data = ""
            if isinstance(value, str):
                for i in value:
                    data += f"{i}%"
                where.append(field.like(data))
            else:
                where.append(field == value)
        
        return self._loads_json(await self.crud.get_data(session, where=where, sorting=sorting, offset=offset, limit=limit))
    
    async def update(self, session, id: int, artist_id: list[int], **fields):
        if fields.get("artists") is not None:
            fields["artists"] = json.dumps(fields["artists"])
        await self.crud.update_data(session, where=[Music.id == id, Music.artists.like(f"%{artist_id}%")], **fields)
    
    async def delete(self, session, id: int, artist_id: int, **fields):
        await self.crud.delete_data(session, id=id, where=[Music.artists.like(f"%{artist_id}%")], **fields)
        
    async def load_depends(self, session, data: list[dict]) -> list[dict]:
        dict_users = {}
        list_user_id = []
        
        for item in data:
            list_user_id.extend(item["artists"])
            
        users = await self.user_crud.get_data(session, where=[User.id.in_(item["artists"])])     
        
        for item in users:
            dict_users[str(item["id"])] = item
        
        for item in data:
            new_users = [dict_users[str(value)] for value in item["artists"]]
            item["artists"] = del_security(*new_users) if new_users else None
            
        return data
    
    def _loads_json(self, data: list[dict]) -> list[dict]:
        for value in data:
            value["artists"] = json.loads(value["artists"])
        return data
    
    def _create_where(self, fields: dict) -> list:
        where = []
        
        for key, value in fields.items():
            field = getattr(Music, key)
            if key == "artists":
                where.append(field.like(f"%{"%".join(str(i) for i in value)}%"))
            else:
                where.append(field == value)
        return where

music_crud = MusicCRUD()