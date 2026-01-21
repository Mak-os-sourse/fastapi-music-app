import time
import json
from numpy import random

from src.app.models.music import Music
from src.app.config import settings

from src.app.tests.utils.session import add_fake_data, get_fake_data
from src.app.tests.utils.user import user_utils
from src.app.tests.fake import fake

class MusicUtils:
    async def add(self, session, n = 1, load_depends: bool = True) -> list[dict]:
        data = [self.fake_data() for _ in range(n)]
        data = await self._dump_data(session, data)

        result = await add_fake_data(session, Music, data)
        result = await self._load_data(session, result, load_depends)

        return result

    async def get(self, session, load_depends: bool = True, **where) -> dict | None:
        result = await get_fake_data(session, Music, **where)
        if result is not None:
            return (await self._load_data(session, [result], load_depends))[0]

    def fake_data(self) -> dict:
        return {"name": fake.name_nonbinary(), "artists": [], "is_private": False,
                "info": "", "genre": settings.MUSIC_GENRES[0], "date_creation": time.time(), "text": "",
                "size_file": random.randint(1, 10000), "duration_sec": random.randint(1, 10000)}
    
    async def _dump_data(self, session, data: list[dict]) -> list[dict]:
        result = data.copy()
        for value in result:
            users = await user_utils.add(session, 4)
            value["artists"] = json.dumps([item["id"] for item in users])
        return result
    
    async def _load_data(self, session, data: list[dict], load_depends: bool) -> list[dict]:
        result = data.copy()
        for value in result:
            users_id = json.loads(value["artists"])
            if load_depends:
                users = [await user_utils.get(session, id=item) for item in users_id]
                value["artists"] = users
            else:
                value["artists"] = users_id
        return result
    
music_utils = MusicUtils()