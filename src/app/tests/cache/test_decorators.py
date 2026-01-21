import asyncio
import time

from src.app.tests.cache import cache
from src.app.tests.config import settings_test

from src.app.caching.decorators import CacheConfig

work_func = 1

async def completion_time(async_func, rc):
    set_time = time.time()
    data = await async_func
    return data, time.time() - set_time, await rc.keys("*")

async def async_func():
    await asyncio.sleep(work_func)
    return "Hello word!"

async def test_cache_async(cache):
    func = cache.cache_func.async_cache()
    func = func(async_func)

    data_set, set_time, key_set = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    
    data_get, get_time, key_get = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    
    assert data_set == data_get == "Hello word!"
    assert len(key_set) == len(key_get) == 1
    assert get_time < work_func
    assert set_time > get_time

async def test_cache_async_by_config(cache):
    @cache.cache_func.async_cache()
    async def func(cache_config: CacheConfig):
        cache_config.key = "main"
        await asyncio.sleep(work_func)
        return "Hello word!"

    data_set, set_time, key_set = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    
    data_get, get_time, key_get = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    
    assert data_set == data_get == "Hello word!"
    assert len(key_set) == len(key_get) == 1
    assert len(await cache.rc.keys("*main*")) == 1
    assert get_time < work_func
    assert set_time > get_time

async def test_cache_exp_async(cache):
    func = cache.cache_func.async_cache(exp=30)
    func = func(async_func)

    data_set, set_time, key_set = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    set_ttl = await cache.rc.ttl(key_set[0])
    
    data_get, get_time, key_get = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    get_ttl = await cache.rc.ttl(key_get[0])
    
    assert data_set == data_get == "Hello word!"
    assert len(key_set) == len(key_get) == 1
    assert get_time < work_func
    assert get_ttl > 20
    assert set_ttl > 20
    assert set_time > get_time
    assert set_ttl >= get_ttl

async def test_cache_exp__update_time_async(cache):
    func = cache.cache_func.async_cache(exp=30, update_time=True)
    func = func(async_func)

    data_set, set_time, key_set = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    set_ttl = await cache.rc.ttl(key_set[0])
    
    await asyncio.sleep(1)
    
    data_get, get_time, key_get = await completion_time(func(response = settings_test.RESPONSE), cache.rc)
    get_ttl = await cache.rc.ttl(key_get[0])
    
    assert data_set == data_get == "Hello word!"
    assert len(key_set) == len(key_get) == 1
    assert get_time < work_func
    assert get_ttl > 20
    assert set_ttl > 20
    assert set_time > get_time
    assert set_ttl <= get_ttl
