import json, time

from src.app.tests.utils.session import add_fake_data, get_fake_data
from src.app.tests.utils.music import music_utils
from src.app.tests.utils.user import user_utils
from src.app.tests.fake import fake

from src.app.models.playlist import PlayList

class PlayListUtils:
    async def add(self, session, n = 1, kind: str = "album",
                  is_private: bool = False, load_depends: bool = True) -> list[dict]:
        data = []
        for _ in range(n):
            data.append(self.fake_data(kind=kind, is_private=is_private))
        data = await self._dump_data(session, data)
            
        result = await add_fake_data(session, PlayList, data)
        result = await self._load_data(session, result, load_depends)
        
        return result
    
    async def get(self, session, load_depends: bool = True, **where) -> dict | None:
        result = await get_fake_data(session, PlayList, **where)
        if result is not None:
            return (await self._load_data(session, [result], load_depends))[0]
    
    def fake_data(self, kind: str = "album", is_private: bool = False) -> dict:
            return {"title": fake.name(), "is_private": is_private, "artist": 0,
                    "music": [], "date_creation": time.time(), "kind": kind}
    
    async def _dump_data(self, session, data: list[dict]) -> list[dict]:
        result = data.copy()
        for value in result:
            user = (await user_utils.add(session))[0]
            music = await music_utils.add(session, 4)
            value["artist"] = user["id"]
            value["music"] = json.dumps([item["id"] for item in music])
        return result
    
    async def _load_data(self, session, data: list[dict], load_depends: bool) -> list[dict]:
        result = data.copy()
        for value in result:
            music_id = json.loads(value["music"])
            if load_depends:
                value["artist"] = await user_utils.get(session, id=value["id"])
                value["music"] = await self._get_music(session, music_id)
            else:
                value["music"] = music_id
        return result

    async def _get_music(self, session, music_id: list[int]) -> list[dict]:
        result = []
        for item in music_id:
            data = await music_utils.get(session, load_depends=False, id=item)
            data.pop("artists")
            result.append(data)
        return result
    
playlist_utils = PlayListUtils()