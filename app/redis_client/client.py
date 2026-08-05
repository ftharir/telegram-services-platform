from __future__ import absolute_import

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_pool, redis_client
    redis_pool = ConnectionPool.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    redis_client = Redis(connection_pool=redis_pool)


async def close_redis() -> None:
    global redis_client, redis_pool
    if redis_client:
        await redis_client.aclose()
    if redis_pool:
        await redis_pool.aclose()