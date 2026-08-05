import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.redis_client.client import close_redis, init_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """مدیریت رویدادهای شروع (Startup) و پایان (Shutdown) برنامه‌ی FastAPI."""
    logger.info("Starting up FastAPI application...")
    await init_redis()
    yield
    logger.info("Shutting down FastAPI application...")
    await close_redis()


def create_app() -> FastAPI:
    """تابع کارخانه‌ای برای ساخت و پیکربندی اپلیکیشن FastAPI."""
    app = FastAPI(
        title="Telegram Services Platform API",
        description="API بک‌اند برای مدیریت خدمات ربات تلگرام و بررسی سلامت سیستم",
        version="1.0.0",
        lifespan=lifespan,
    )

    # تنظیمات CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ثبت روترهای API
    app.include_router(api_v1_router, prefix="/api")

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Telegram Services Platform API is running!",
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()