import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.session import get_async_session
from app.redis_client.client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict:
    """تست زنده بودن اپلیکیشن (Liveness Probe)."""
    return {
        "status": "ok",
        "service": "telegram-services-platform",
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(session: AsyncSession = Depends(get_async_session)) -> dict:
    """بررسی آمادگی کامل سیستم و صحت اتصالات PostgreSQL و Redis (Readiness Probe)."""
    components = {
        "database": "unknown",
        "redis": "unknown",
    }

    # ۱. تست اتصال به دیتابیس PostgreSQL
    try:
        await session.execute(text("SELECT 1"))
        components["database"] = "healthy"
    except Exception as e:
        logger.error("Readiness check DB failure: %s", e)
        components["database"] = "unhealthy"

    # ۲. تست اتصال به Redis
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        components["redis"] = "healthy"
    except Exception as e:
        logger.error("Readiness check Redis failure: %s", e)
        components["redis"] = "unhealthy"

    # تعیین وضعیت کلی
    is_ready = all(status_val == "healthy" for status_val in components.values())

    return {
        "status": "ready" if is_ready else "degraded",
        "components": components,
    }