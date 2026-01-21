from src.app.config import settings

def key_cache_func(data: str) -> str:
    return f"{settings.PREFIX_CACHE_FUNC}-{settings.NAMESPACE_USER}:-{data}"