import pickle

from src.app.cache import rc

class Cache:
    def __init__(self, rc):
        self.rc = rc

    async def set(self, key: str, value: dict, exp: int = None):
        data = await self.rc.set(key, pickle.dumps(value))
        
        if exp is not None:
            await self.rc.expire(key, exp)

        return data
    
    async def get(self, key: str):
        data = await self.rc.get(key)
        
        if data is not None:
            return pickle.loads(data)

    async def get_ttl(self, name: str):
        return await self.rc.ttl(name)

    async def get_keys(self, match: str = None, offset: int = 0, limit: int = 10):
        if match is not None:
            data = await self.rc.scan(offset, match=match, count=limit)
        else:
            data = await self.rc.scan(offset, count=limit)
        
        data = list(data)
        data[1] = [i.decode() for i in data[1]]
        return tuple(data)
        
    async def get_all_keys(self, name: str):
        data = await self.rc.keys(name)
        
        return [i.decode() for i in data]

    async def delete(self, *name):
        return await self.rc.delete(*name)

class LruCache(Cache):
    def __init__(self, rc, max_time=3600):
        super().__init__(rc)
        self.max_time = max_time
    
    def async_cache(self, exp):
        def decorator(func):
            def wrapper(*args, **kwargs):
                @Cache.async_cache(self, exp=exp)
                async def wrapped(*args, **kwargs):
                    return await func(*args, **kwargs)
                data = wrapped(*args, **kwargs)
                print(data.__module__)
                self.rc.expire(f"func-cache-{Cache._hash_func(self, data, *args, **kwargs)}")
                return data
            return wrapper
        return decorator
    
    async def set(self, key: str, value: dict):
        return await super().set(key, value, self.max_time)

    async def get(self, key: str):
        data = await super().get(key)
        await self.rc.expire(key, self.max_time)
        return data

cache = Cache(rc)
lru_cache = LruCache(rc, max_time=1800)