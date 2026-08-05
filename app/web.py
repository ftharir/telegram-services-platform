import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات وب‌سرور FastAPI."""
    logger.info("Starting up FastAPI application...")
    yield
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="Telegram Services Platform API",
    description="Backend Web API for Telegram Bot Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ثبت مسیرهای API
app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": "Telegram Services Platform API is running"}