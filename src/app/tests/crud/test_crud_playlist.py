import json

from src.app.tests.utils.playlist import playlist_utils
from src.app.tests.utils.music import music_utils
from src.app.tests.utils.user import user_utils
from src.app.tests.db import metadata, session

from src.app.models.playlist import PlayList, PlayListModel
from src.app.models.user import UserModel
from src.app.crud.playlist import playlist_crud
from src.app.utils.user import del_security
from src.app.tests.fake import fake

async def test_add_playlist(session):
    album = playlist_utils.fake_data()

    result = await playlist_crud.add(session, title=album["title"], music=album["music"],
                                  artist=album["artist"], is_private=album["is_private"], kind="album")
    
    assert result[PlayListModel.kind] == "album"
    assert result[PlayListModel.title] == album[PlayListModel.title]
    assert result[PlayListModel.artist] == album[PlayListModel.artist]
    assert json.loads(result[PlayListModel.music]) == album[PlayListModel.music]
    assert result[PlayListModel.is_private] == album[PlayListModel.is_private]
    
async def test_get_album(session):
    album = (await playlist_utils.add(session, load_depends=False))[0]

    result = await playlist_crud.get(session, id=album[PlayListModel.id])
    result = result[0]
    
    assert result == album
    
async def test_search_album(session):
    album = (await playlist_utils.add(session, 6, load_depends=False))[0]
    name = album[PlayListModel.title][:len(album[PlayListModel.title]) - 1]
    
    result = await playlist_crud.search(session, title=name)
    result = result[0]
    
    assert result == album
    
async def test_search_music_by_sorting(session):
    await playlist_utils.add(session, 6)
    
    result = await playlist_crud.search(session, sorting=[(PlayList.id, True)])
    
    assert result == sorted(result, key=lambda x: x[PlayListModel.id], reverse=True)

async def test_update_album(session):
    album = (await playlist_utils.add(session))[0]
    new_title = fake.name_nonbinary()
    
    await playlist_crud.update(session, id=album[PlayListModel.id],
                               artist_id=album[PlayListModel.artist][UserModel.id],
                               title=new_title)
    
    result = await playlist_utils.get(session, id=album[PlayListModel.id])

    assert result[PlayListModel.title] == new_title

async def test_delete_album(session):
    album = (await playlist_utils.add(session))[0]
    
    await playlist_crud.delete(session, id=album[PlayListModel.id])
    
    result = await playlist_utils.get(session, id=album[PlayListModel.id])
    
    assert result is None

async def test_load_depends(session):
    album = (await playlist_utils.add(session))[0]
    album[PlayListModel.artist] = del_security(album[PlayListModel.artist])[0]
    data = album.copy()
    data[PlayListModel.artist] = data[PlayListModel.artist][UserModel.id]
    data[PlayListModel.music] = [value[UserModel.id] for value in data[PlayListModel.music]]
    
    result = await playlist_crud.load_depends(session, [data])
    
    assert result[0] == album