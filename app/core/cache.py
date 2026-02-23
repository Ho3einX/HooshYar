from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


def get_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_DSN, decode_responses=True)
