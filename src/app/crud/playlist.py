import json
from datetime import datetime, timezone

from src.app.models.playlist import PlayList, PlayListModel
from src.app.utils.user import del_security
from src.app.models.user import UserModel
from src.app.models.music import MusicModel
from src.app.crud.base import CRUD
from src.app.models.user import User
from src.app.models.music import Music

class PlayListCRUD:
    def __init__(self):
        self.crud = CRUD(PlayList)
        self.music_crud = CRUD(Music)
        self.user_crud = CRUD(User)
        
    async def add(self, session, title: str, music: list,
                  artist: int, kind: str, is_private: bool = False) -> dict:
        return await self.crud.add_data(session, title=title, music=json.dumps(music), artist=artist, kind=kind,
                                        is_private=is_private, date_creation=int(datetime.now(timezone.utc).timestamp()))
    
    async def get(self, session, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = self._create_where(fields)
        
        result = await self.crud.get_data(session, where=where, offset=offset, limit=limit)
        return self._loads_json(result)
        
    async def search(self, session, sorting: list[tuple[object, bool]] = None, offset: int = 0, limit: int = 10, **fields) -> list[dict]:
        where = []
        
        for key, value in fields.items():
            field = getattr(PlayList, key)
            data = ""
            if isinstance(value, str):
                for char in value:
                    data += f"{char}%"
                where.append(field.like(data))
            else:
                where.append(field == value)
        
        result = await self.crud.get_data(session, where=where, sorting=sorting, offset=offset, limit=limit)
        return self._loads_json(result)
    
    async def update(self, session, id: int, artist_id: list[int], **fields):
        if fields.get(PlayListModel.music) is not None:
            fields[PlayListModel.music] = json.dumps(fields[PlayListModel.music])
        await self.crud.update_data(session, where=[PlayList.id == id, PlayList.artist.like(f"%{artist_id}%")], **fields)
    
    async def delete(self, session, id: int, **fields):
        await self.crud.delete_data(session, id=id, **fields)
    
    async def load_depends(self, session, data: list[PlayList],
                           offset: int = 0, limit: int = 10,
                           sorting: list[tuple[object, bool]] = None) -> list[PlayList]:
        dict_users, dict_music = self._extract_depends(data)
            
        music = await self.music_crud.get_data(session, where=[Music.id.in_(list(dict_music.keys()))],
                                                offset=offset, limit=limit, sorting=sorting)
        users = await self.user_crud.get_data(session, where=[User.id.in_(list(dict_users.keys()))])
        
        for item in users:
            dict_users[str(item[UserModel.id])] = item
        for item in music:
            item.pop(MusicModel.artists)
            dict_music[str(item[MusicModel.id])] = item
        
        for item in data:
            new_music = [dict_music.get(str(value)) for value in item[PlayListModel.music]]
            new_user = dict_users.get(str(item[PlayListModel.artist]))
            
            item[PlayListModel.music] = new_music
            item[PlayListModel.artist] = del_security(new_user)[0] if new_user else None
            
        return data
    
    def _extract_depends(self, data: list[PlayList]) -> tuple[dict, dict]:
        dict_users = {}
        dict_music = {}
        
        for item in data:
            for value in item[PlayListModel.music]:
                dict_music[value] = None
            dict_users[item[PlayListModel.artist]] = None
        
        return dict_users, dict_music
    
    def _loads_json(self, data: list[PlayList]) -> list[PlayList]:
        for value in data:
            value[PlayListModel.music] = json.loads(value[PlayListModel.music])  
        return data
    
    def _create_where(self, fields: dict) -> list:
        where = []
        
        for key, value in fields.items():
            field = getattr(PlayList, key)
            if key == PlayListModel.music:
                where.append(field.like(f"%{"%".join(str(i) for i in value)}%"))
            else:
                where.append(field == value)
        return where

playlist_crud = PlayListCRUD()