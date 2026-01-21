import json

from src.app.crud.music import music_crud
from src.app.models.music import Music

from src.app.tests.utils.music import music_utils
from src.app.utils.user import del_security
from src.app.tests.db import metadata, session
from src.app.tests.fake import fake

async def test_add_music(session):
    music = music_utils.fake_data()
    
    result = await music_crud.add(session, name=music["name"], genre=music["genre"], artists=music["artists"],
                                  size_file=music["size_file"], duration_sec=music["duration_sec"], text=music["text"],
                                  is_private=music["is_private"])
    
    assert result["name"] == music["name"].lower()
    assert result["info"] == music["info"]
    assert result["text"] == music["text"]
    assert result["genre"] == music["genre"]
    assert json.loads(result["artists"]) == music["artists"]
    assert result["size_file"] == music["size_file"]
    assert result["is_private"] == music["is_private"]
    assert result["duration_sec"] == music["duration_sec"]

async def test_get_music(session):
    music = (await music_utils.add(session, load_depends=False))[0]
    
    result = await music_crud.get(session, id=music["id"])
    result = result[0]
    
    assert result == music
    
async def test_search_music(session):
    music = (await music_utils.add(session, 6, load_depends=False))[0]
    
    result = await music_crud.search(session, name=music["name"][:len(music["name"]) - 1])
    result = result[0]
    
    assert result == music
    
async def test_search_music_by_sorting(session):
    await music_utils.add(session, 6)
    
    result = await music_crud.search(session, sorting=[(Music.id, True)])
    
    assert result == sorted(result, key=lambda x: x["id"], reverse=True)

async def test_update_music(session):
    music = (await music_utils.add(session))[0]
    new_name = fake.name_nonbinary()
    
    await music_crud.update(session, id=music["id"], artist_id=music["artists"][0]["id"], name=new_name)
    
    result = await music_utils.get(session)

    assert result["name"] in new_name

async def test_delete_music(session):
    music = (await music_utils.add(session))[0]
    
    await music_crud.delete(session, artist_id=music["artists"][0]["id"], id=music["id"])
    
    result = await music_utils.get(session, id=music["id"])
    
    assert result == None
    
async def test_load_depends(session):
    music = (await music_utils.add(session))[0]
    music["artists"] = del_security(*music["artists"])
    data = music.copy()
    data["artists"] = [value["id"] for value in data["artists"]]
    
    result = await music_crud.load_depends(session, [data])
    
    assert result[0] == music