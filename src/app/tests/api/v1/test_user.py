from src.app.tests.utils.client import overrides_user_auth
from src.app.tests.utils.files import await_file, cp_file
from src.app.tests.utils.cache import key_cache_func
from src.app.tests.utils.user import user_utils
from src.app.tests.config import settings_test
from src.app.tests.db import metadata, session
from src.app.tests.client import client
from src.app.tests.cache import cache
from src.app.tests.fake import fake

from src.app.api.v1.endpoints.user import UserAPI
from src.app.models.user import UserModel
from src.app.config import settings

async def test_get_user(cache, session, client):
    user = (await user_utils.add(session))[0]
    
    result = client.get(UserAPI.GET.paste(id=user[UserModel.id]))
    
    assert result.status_code == 200
    assert result.json() == user
    assert len(await cache.rc.keys()) == 1
    
async def test_get_me(cache, session, client):
    user = (await user_utils.add(session))[0]
    
    overrides_user_auth(user)
    
    result = client.get(UserAPI.ME)

    assert result.status_code == 200
    assert result.json() == user
    assert len(await cache.rc.keys()) == 1

async def test_search(cache, session, client):
    user = (await user_utils.add(session, 6))[0]
    
    username = user["username"][:len(user["username"]) - 3]
    
    result = client.get(UserAPI.SEARCH, params={"field": f"username:{username}"})
    
    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0] == user
    assert len(await cache.rc.keys()) == 1
    
async def test_sorting_search(cache, session, client):
    count_users = 6
    users = (await user_utils.add(session, count_users))
    
    result = client.get(UserAPI.SEARCH, params={"sorting": "id:True"})
    data = result.json()

    users = sorted(users, reverse=True, key=lambda item: item["id"])

    assert result.status_code == 200
    assert len(data) == count_users
    assert len(await cache.rc.keys()) == 1
    assert [i == j for i, j in zip(users, data)]
    
async def test_update_data(cache, session, client):
    user = (await user_utils.add(session))[0]
    new_name = fake.name()

    await cache.rc.set(key_cache_func(f"id:{user["id"]}"), "")
    overrides_user_auth(user)

    result = client.put(UserAPI.UPDATE, json={"field": f"name:{new_name}"})
    
    update = await user_utils.get(session, id=user["id"])

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert update[UserModel.name] == new_name
    assert len(await cache.rc.keys()) == 0

async def test_set_image(cache, session, client):
    user = (await user_utils.add(session))[0]
    path = settings.PATH_USER_IMAGE / f"{user["id"]}.{settings.BASE_FORMAT_IMAGE}"
    
    await cache.rc.set(key_cache_func(f"user-image:id:{user["id"]}"), "")
    overrides_user_auth(user)
    
    result = client.post(UserAPI.SET_IMAGE, files={"image": open(settings_test.PATH_FILES / "image.jpg", "rb")})

    assert result.status_code == 200
    assert result.json() == settings.STATUS_OK
    assert len(await cache.rc.keys()) == 0
    assert await await_file(path)
    path.unlink()

async def test_fail_set_image(session, client):
    user = (await user_utils.add(session))[0]
    overrides_user_auth(user)
    
    result = client.post(UserAPI.SET_IMAGE, files={"image":
        open(settings_test.PATH_FILES / "test_file.txt", "rb")})

    assert result.status_code == 400

async def test_get_image(cache, client):
    path = settings_test.PATH_FILES / "image.png"
    path_copy = settings.PATH_USER_IMAGE / f"1000.{settings.BASE_FORMAT_IMAGE}"
    await cp_file(path, path_copy)
    
    result = client.get(UserAPI.GET_IMAGE.paste(id=1000))

    assert result.status_code == 200
    assert result.content == open(path_copy, "rb").read()
    assert await cache.rc.keys(f"*id:{1000}*")
    path_copy.unlink()