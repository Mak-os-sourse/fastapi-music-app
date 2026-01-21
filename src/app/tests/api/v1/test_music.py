import json
from sqlalchemy import select

from src.app.tests.utils.music import fake_music_data, add_music
from src.app.tests.utils.user import add_users
from src.app.tests.utils.files import await_file
from src.app.tests.utils.user import fake_user
from src.app.tests.config import settings_test
from src.app.tests.client import client
from src.app.tests.cache import cache
from src.app.tests.db import session
from src.app.tests.fake import fake

from src.app.utils.user import del_security
from src.app.depends.auth import auth_user
from src.app.models.music import Music
from src.app.config import settings
from src.app.app import app

async def test_add_music(session, client):
    app.dependency_overrides[auth_user] = lambda: {"id": music_data["artists"][0], **fake_user()}
    music_data = fake_music_data()

    result = client.post(f"{settings_test.MUSIC_PATH}/add/music/", json={"name": music_data["name"], "genre": music_data["genre"],
                                                          "info":  music_data["info"], "text": music_data["text"],
                                                          "is_private": music_data["is_private"]})
    
    stmt = await session.scalars(select(Music).where(Music.name == music_data["name"].lower()))
    data = stmt.one()

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert data.name == music_data["name"].lower()
    assert data.genre == music_data["genre"]
    assert data.info == music_data["info"]
    assert data.text == music_data["text"]
    assert json.loads(data.artists)[0] == music_data["artists"][0]
    assert data.is_private == music_data["is_private"]
    
async def test_get_genre(cache, client):
    result = client.get(f"{settings_test.MUSIC_PATH}/genres/get/")
    
    assert result.status_code == 200
    assert result.json() == settings.MUSIC_GENRES
    assert len(await cache.rc.keys()) == 1

async def test_get_music_audio(client):
    path = settings_test.PATH_FILES / f"{1000}.{settings.BASE_FORMAT_MUSIC}"
    start = 100
    end = path.stat().st_size
    
    with open(path, "rb") as file:
        file.seek(start)
        data = file.read(end)
    
    result = client.get(f"{settings_test.MUSIC_PATH}/get/audio/{1000}/", params={"start": start, "end": end})
    
    assert result.status_code == 200
    assert result.content == data
    
async def test_get_none_music_audio(client):
    result = client.get(f"{settings_test.MUSIC_PATH}/get/audio/{0}/", params={"start": 0, "end": 0})
    
    assert result.status_code == 200
    assert result.json() is None

async def test_get_music_cover(client):
    path = settings_test.PATH_FILES / f"{1000}.{settings.BASE_FORMAT_IMAGE}"
    
    data = open(path, "rb").read()
    
    result = client.get(f"{settings_test.MUSIC_PATH}/get/cover/{1000}/")
    
    assert result.status_code == 200
    assert result.content == data

async def test_get_none_music_cover(client):
    result = client.get(f"{settings_test.MUSIC_PATH}/get/cover/{0}/")
    
    assert result.status_code == 200
    assert result.json() is None

async def test_get_music(session, client):
    user = (await add_users(session))[0]
    music = (await add_music(session, artists=[user["id"]]))[0]
    music["artists"] = del_security(user)
    
    result = client.get(f"{settings_test.MUSIC_PATH}/get/{music["id"]}/")

    assert result.status_code == 200
    assert result.json() == music
    
async def test_search_music(session, client):
    user = (await add_users(session))[0]
    music = (await add_music(session, artists=[user["id"]]))[0]
    music["artists"] = del_security(user)
    
    name = music["name"][:len(music["name"]) - 3]
    
    result = client.get(f"{settings_test.MUSIC_PATH}/search/", params={"field": f"name:{name}"})

    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0] == music
    
async def test_sorting_search(session, client):
    music = (await add_music(session, 6))
    
    result = client.get(f"{settings_test.MUSIC_PATH}/search/", params={"sorting": "id:True"})

    music = sorted(music, reverse=True, key=lambda item: item["id"])

    assert result.status_code == 200
    assert len(result.json()) == 6
    for i, j in zip(music, result.json()):
        assert i["id"] == j["id"]
        
async def test_update_music_data(session, client):
    music = (await add_music(session))[0]
    new_info = fake.text()
    
    app.dependency_overrides[auth_user] = lambda: {"id": music["artists"], **fake_user()}
    
    result = client.put(f"{settings_test.MUSIC_PATH}/update/data/", params={"id": music["id"]}, json={"field": f"info:{new_info}"})
    
    stmt = await session.scalars(select(Music).where(Music.id == music["id"]))
    update = stmt.one()
    
    assert result.status_code == 200
    assert update.info == new_info
    
async def test_add_file_music(session, client):
    music = (await add_music(session))[0]
    music_path = settings_test.PATH_FILES / f"{music["id"]}.{settings.BASE_FORMAT_MUSIC}"
    cover_path = settings_test.PATH_FILES / f"{music["id"]}.{settings.BASE_FORMAT_IMAGE}"
    
    app.dependency_overrides[auth_user] = lambda: {"id": music["artists"], **fake_user()}
    
    result = client.put(f"{settings_test.MUSIC_PATH}/set/files/", params={"id": music["id"]},
                        files={"cover": open(settings_test.PATH_FILES / "test_image.jpg", "rb"),
                               "music": open(settings_test.PATH_FILES / "test_music.wav", "rb")})

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert await await_file(music_path)
    assert await await_file(cover_path)
    music_path.unlink()
    cover_path.unlink()
    
async def test_delete_music(session, client):
    music = (await add_music(session))[0]
    app.dependency_overrides[auth_user] = lambda: {"id": music["artists"][0], **fake_user()}
    music_path = settings_test.PATH_FILES / f"{music["id"]}.{settings.BASE_FORMAT_MUSIC}"
    cover_path = settings_test.PATH_FILES / f"{music["id"]}.png"

    with open(cover_path, "wb") as file:
        file.write(open(settings_test.PATH_FILES / "1000.png", "rb").read())
    
    with open(music_path, "wb") as file:
        file.write(open(settings_test.PATH_FILES / "1000.mp3", "rb").read())
    
    result = client.delete(f"{settings_test.MUSIC_PATH}/delete/", params={"id": music["id"]})
    
    stmt = await session.scalars(select(Music).where(Music.id == music["id"]))
    delete = stmt.all()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert delete == []
    assert not music_path.exists()
    assert not cover_path.exists()
