from redis.asyncio import Redis

from src.app.config import settings

rc = Redis(host=settings.CACHE_HOST, port=settings.CACHE_PORT)