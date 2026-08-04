from typing import Optional  
from redis.asyncio import Redis, ConnectionPool  
from app.core.config import settings  
from app.core.logging import get_logger  


logger = get_logger(__name__)


redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """راه‌اندازی استخر اتصالات و ساخت شیء کلاینت Redis.
    
    Returns:
        Redis: شیء فعال کلاینت Redis جهت انجام عملیات‌ها.
    """
    global redis_pool, redis_client
    
    
    if redis_client is not None:
        return redis_client

    try:
        
        redis_pool = ConnectionPool.from_url(
            settings.redis_url,  
            decode_responses=True,  
            max_connections=20,  
        )
        
        
        redis_client = Redis(connection_pool=redis_pool)
        
        
        await redis_client.ping()
        logger.info("Successfully connected to Redis server.")
        
        return redis_client
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis server: {e}")
        raise e


async def get_redis() -> Redis:
    """دریافت کلاینت فعال Redis (اگر متصل نشده باشد، ابتدا متصل می‌شود).
    
    Returns:
        Redis: شیء فعال Redis.
    """
    if redis_client is None:
        return await init_redis()
    return redis_client


async def close_redis() -> None:
    """بستن امن اتصالات Redis هنگام خاموش شدن برنامه."""
    global redis_pool, redis_client
    
    if redis_client is not None:
        
        await redis_client.aclose()
        redis_client = None
        
    if redis_pool is not None:
        
        await redis_pool.disconnect()
        redis_pool = None
        
    logger.info("Redis connections closed successfully.")
    