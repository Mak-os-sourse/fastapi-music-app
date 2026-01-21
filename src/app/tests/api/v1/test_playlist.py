import json
from sqlalchemy import select

from src.app.tests.utils.playlist import fake_playlist_data, add_playlist
from src.app.tests.utils.music import add_music
from src.app.tests.utils.user import add_users
from src.app.tests.utils.user import fake_user
from src.app.tests.config import settings_test
from src.app.tests.client import client
from src.app.tests.db import session
from src.app.tests.fake import fake

from src.app.utils.user import del_security
from src.app.depends.auth import auth_user
from src.app.models.playlist import PlayList
from src.app.config import settings
from src.app.app import app

async def test_create_album(session, client):
    playlist = fake_playlist_data()
    
    app.dependency_overrides[auth_user] = lambda: {"id":  playlist["artist"], **fake_user()}
    
    result = client.post(f"{settings_test.USER_DATA_PATH}/album/create/", json={"title": playlist["title"], "is_private": playlist["is_private"]})
    
    stmt = await session.scalars(select(PlayList).where(PlayList.title == playlist["title"]))
    data = stmt.one()
    
    assert result.status_code == 200
    assert data.title == playlist["title"]
    assert data.artist == playlist["artist"]
    assert json.loads(data.music) == []
    assert data.is_private == playlist["is_private"]

async def test_fail_create_album(session, client):
    playlist = (await add_playlist(session))[0]
    
    app.dependency_overrides[auth_user] = lambda: {"id":  playlist["artist"], **fake_user()}
    
    result = client.post(f"{settings_test.USER_DATA_PATH}/Album/create/", json={"title": playlist["title"], "is_private": playlist["is_private"]})
    
    assert result.status_code == 409
    
async def test_add_music(session, client):
    playlist = (await add_playlist(session))[0]
    music = await add_music(session, artists=[playlist["artist"]])
    new_item = [1]

    app.dependency_overrides[auth_user] = lambda: {"id": playlist["artist"], **fake_user()}
    
    result = client.post(f"{settings_test.USER_DATA_PATH}/album/add/", json={"id": playlist["id"], "music": new_item})
    
    stmt = await session.scalars(select(PlayList).where(PlayList.title == playlist["title"]))
    data = stmt.one()

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert len(data.music) > len(new_item)
    assert new_item[0] == json.loads(data.music)[-1]
    
async def test_add_music_like(session, client):
    playlist = fake_playlist_data(kind="like")
    new_item = [1]

    app.dependency_overrides[auth_user] = lambda: {"id": playlist["artist"], **fake_user()}
    
    result = client.post(f"{settings_test.USER_DATA_PATH}/Like/add/", json={"id": 0, "music": new_item})
    
    stmt = await session.scalars(select(PlayList).where(PlayList.kind == playlist["kind"]))
    data = stmt.one()

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert json.loads(data.music)[0] == new_item[0]
    
async def test_fail_add_music(client):
    album = fake_playlist_data()
    
    app.dependency_overrides[auth_user] = lambda: {"id": album["artist"], **fake_user()}

    result = client.post(f"{settings_test.USER_DATA_PATH}/album/add/", json={"id": 1, "music": [1]})

    assert result.status_code == 409

async def test_delete_album_music(session, client):
    album = (await add_playlist(session))[0]
    new_music = album["music"].copy()
    music_id = new_music.pop(1)
    
    app.dependency_overrides[auth_user] = lambda: {"id": album["artist"], **fake_user()}

    result = client.delete(f"{settings_test.USER_DATA_PATH}/album/delete/music/", params={"id": album["id"],
                                                                                          "music_id": music_id})
    
    stmt = await session.scalars(select(PlayList).where(PlayList.title == album["title"]))
    data = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert json.loads(data.music) == new_music

async def test_fail_delete_album_music(client):
    album = fake_playlist_data()
    music_id = album["music"][0]
    
    app.dependency_overrides[auth_user] = lambda: {"id": album["artist"], **fake_user()}
    
    result = client.delete(f"{settings_test.USER_DATA_PATH}/album/delete/music/", params={"id": 1, "music_id": music_id})
    
    assert result.status_code == 409
  
async def test_get_user_data(session, client):
    user = (await add_users(session))[0]
    music = (await add_music(session))[0]
    album = (await add_playlist(session, music=[music["id"]], artist=user["id"]))[0]
    album["music"] = [music]
    album["artist"] = del_security(user)[0]
    music.pop("artists")
    
    result = client.get(f"{settings_test.USER_DATA_PATH}/album/get/", params={"field": f"artist:{user["id"]}"})

    assert result.status_code == 200
    assert result.json()[0] == album
    
async def test_get_my_album(session, client):
    user = (await add_users(session))[0]
    music = (await add_music(session))[0]
    album = (await add_playlist(session, music=[music["id"]], artist=user["id"], is_private=True))[0]
    album["music"] = [music]
    album["artist"] = del_security(user)[0]
    music.pop("artists")
    
    app.dependency_overrides[auth_user] = lambda: {"id": user["id"], **fake_user()}

    result = client.get(f"{settings_test.USER_DATA_PATH}/album/get/my/")

    assert result.status_code == 200
    assert result.json()[0] == album
    
async def test_search_album(session, client):
    user = (await add_users(session))[0]
    music = (await add_music(session))[0]
    album = (await add_playlist(session, music=[music["id"]], artist=user["id"]))[0]
    album["music"] = [music]
    album["artist"] = del_security(user)[0]
    title = album["title"]
    music.pop("artists")
    
    result = client.get(f"{settings_test.USER_DATA_PATH}/album/search/", params={"field": f"title:{title[:len(title)-2]}"})

    assert result.status_code == 200
    assert result.json()[0] == album

async def test_update_album(session, client):
    album = (await add_playlist(session))[0]
    new_title = fake.name_nonbinary()
    
    app.dependency_overrides[auth_user] = lambda: {"id": album["artist"], **fake_user()}
    
    result = client.put(f"{settings_test.USER_DATA_PATH}/album/update/data/", params={"id": album["id"]}, json={"field": f"title:{new_title}"})

    stmt = await session.scalars(select(PlayList).where(PlayList.title == new_title))
    data = stmt.one()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert data.title == new_title

async def test_delete_album(session, client):
    album = (await add_playlist(session))[0]
    
    app.dependency_overrides[auth_user] = lambda: {"id": album["artist"], **fake_user()}
    
    result = client.delete(f"{settings_test.USER_DATA_PATH}/album/delete/", params={"id": album["id"]})

    stmt = await session.scalars(select(PlayList).where(PlayList.id == album["id"]))
    data = stmt.all()
    
    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert data == []