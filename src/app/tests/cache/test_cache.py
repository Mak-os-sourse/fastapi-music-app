import pickle

from src.app.tests.fake import fake
from src.app.tests.cache import cache

async def test_cache_set(cache):
    result = await cache.cache.set(key="user", value={"mame": fake.name()})
    assert result == 1
    
    result = await cache.cache.set(key="user", value={"mame": fake.name()}, exp=30)
    assert result == 1
    assert await cache.rc.ttl("user")

async def test_cache_get(cache):
    name = fake.name()
    
    await cache.rc.set(name="user", value=pickle.dumps(name))
    result = await cache.cache.get("user")

    assert result == name

async def test_cache_get_keys(cache):
    args = [{"offset": 0, "limit": 5}, {"offset": 5, "limit": 10}, {"offset": 0, "limit": 5, "match": "u"}]

    keys = []
    
    for i in range(10):
        keys.append(f"{i} age")
        await cache.rc.set(name=f"{i} age", value=i)
    
    for i in args:
        result = await cache.cache.get_keys(**i)

        for i in result[1]:
            assert i in keys

async def test_get_all_keys(cache):
    keys = []
    for i in range(10):
        keys.append(f"{i}")
        await cache.rc.set(name=f"{i}", value=i)
    
    data = await cache.cache.get_all_keys("*")
    
    for i in data:
        assert i in keys

async def test_cache_delete(cache):
    await cache.rc.set(name="name", value=fake.name())
    
    result = await cache.cache.delete("name")

    assert result == 1
    
async def test_lru_cache_set(cache):
    result = await cache.lru_cache.set(key="user", value={"mame": fake.name()})
    
    assert result == 1
    assert cache.rc.ttl("user") != -1

async def test_lru_cache_get(cache):
    value = {"name": fake.name()}

    await cache.rc.set(name="user", value=pickle.dumps(value))
    result = await cache.lru_cache.get("user")

    assert await cache.rc.ttl("user") != 1
    assert result == value