import pytest_asyncio

from redis.asyncio import Redis

from src.app.cache import rc
from src.app.caching.decorators import CacheFunc
from src.app.caching.cache import LruCache, Cache

class CacheTest():
    def __init__(self):
        self.rc = Redis()
        
        self.cache_func = CacheFunc(self.rc)
        self.lru_cache = LruCache(self.rc, max_time=10)
        self.cache = Cache(self.rc)
     
@pytest_asyncio.fixture()
async def cache():
    cache_test = CacheTest()
    await cache_test.rc.flushall()
    yield cache_test
    await cache_test.rc.flushall()
    await cache_test.rc.aclose()

@pytest_asyncio.fixture()
async def close_pool():
    yield 
    await rc.aclose()