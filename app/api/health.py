import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.session import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check(session: AsyncSession = Depends(get_async_session)) -> dict:
    """بررسی وضعیت سلامت وب‌سرور و اتصال به دیتابیس PostgreSQL."""
    db_status = "healthy"
    try:
        # اجرای کوئری ساده برای تست اتصال دیتابیس
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Health check DB failure: %s", e)
        db_status = "unhealthy"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "service": "telegram-services-platform",
    }