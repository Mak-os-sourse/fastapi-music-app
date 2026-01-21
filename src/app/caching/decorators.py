import hashlib
import inspect
import pickle
import time
from fastapi import Response

from src.app.config import settings
from src.app.cache import rc

class CacheConfig:
    def __init__(self):
        self.key = ""

class CacheFunc:
    def __init__(self, rc, prefix = settings.PREFIX_CACHE_FUNC):
        self.rc = rc
        self.prefix = prefix
    
    def async_cache(self, exp: int = None, update_time: bool = False, namespace: str = ""):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                response = kwargs.pop("response")
                cache_config = CacheConfig()
                time_start = time.time()
                
                key = self.get_key(func, *args, **kwargs, namespace=namespace)

                name = (await self.rc.keys(f"{key}*"))
                result = await self.rc.get(name[0]) if name else None
                result = pickle.loads(result) if result is not None else None

                if result is None:
                    self._search_config(func, kwargs, cache_config)
                        
                    result = await func(*args, **kwargs)
                    key = f"{key}-{cache_config.key}"

                    await self.rc.set(key, pickle.dumps(result))
                    response.headers["X-CACHE-STATUS"] = "SET"
                    if exp is not None:
                        await self.rc.expire(key, exp)
                else:
                    response.headers["X-CACHE-STATUS"] = "GET"
                    if exp is not None:
                        if update_time:
                            await self.rc.expire(name[0], exp)
                            
                response.headers["X-TIME-WORK"] = str(time.time()- time_start)
                return result
            return self._set_signature(wrapper, func)
        return decorator
    
    async def delete(self, match: str, namespace: str = ""):
        keys = await self.rc.keys(f"{self.prefix}-{namespace}:*-*{match}")
        for key in keys:
            await self.rc.delete(key)
    
    def get_key(self, callback, namespace, *args, **kwargs):
        return f"{self.prefix}-{namespace}:{self._hash_func(callback, *args, **kwargs)}"
                
    def _search_config(self, func, kwargs, cache_config):
        for param in inspect.signature(func).parameters.values():
            if param.annotation == CacheConfig or param.default == CacheConfig:
                kwargs[param.name] = cache_config
    
    def _hash_func(self, func, *args, **kwargs):
        type_list = (int, str, bool, list, tuple, set, float, dict)
        
        func_args = {"kwargs": kwargs, "args": list(args)}
        for key, value in func_args["kwargs"].items():
            if type(value) not in type_list:
                try:
                    func_args["kwargs"][key] = getattr(value, "model_dump")()
                except AttributeError:
                    func_args["kwargs"][key] = type(value)
        for value in func_args["args"]:
            if type(value) not in type_list:
                func_args["args"][func_args["args"].index(value)] = type(value)
            
        data = {"name": func.__name__, "module": func.__module__, "args": str(func_args)}

        return hashlib.sha256(pickle.dumps(data)).hexdigest()

    def _set_signature(self, wrapper, func):
        sig = inspect.signature(wrapper)
        new_params = []
        
        for param in inspect.signature(func).parameters.values():
            new_params.append(inspect.Parameter(name=param.name, default=param.default, annotation=param.annotation, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD))
            
        new_params.append(inspect.Parameter(name="response", kind=inspect.Parameter.KEYWORD_ONLY, annotation=Response))
        wrapper.__signature__ = sig.replace(parameters=new_params)
        return wrapper

cache_func = CacheFunc(rc)