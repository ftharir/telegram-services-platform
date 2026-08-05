import asyncio
import sys
import uvicorn

from app.core.logging import get_logger
from app.core.shutdown import graceful_shutdown, register_shutdown_callback
from app.database.session import engine
from app.redis_client.client import close_redis
from app.main import main as start_bot
from app.web import app as fastapi_app

logger = get_logger(__name__)


async def close_db_engine() -> None:
    """بستن موتور اتصالات دیتابیس PostgreSQL."""
    logger.info("Disposing database engine connections...")
    await engine.dispose()


async def start_web_server() -> None:
    """راه‌اندازی سرور وب Uvicorn به‌صورت Async."""
    config = uvicorn.Config(
        app=fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    logger.info("Starting Uvicorn Web Server on http://0.0.0.0:8000...")
    await server.serve()


async def main() -> None:
    """اجرای همزمان و موازی ربات تلگرام و وب‌سرور FastAPI همراه با Graceful Shutdown."""
    logger.info("Starting Telegram Services Platform (Bot + Web API)...")
    
    # ثبت توابع پاکسازی منابع دیتابیس و ردیس
    register_shutdown_callback(close_redis)
    register_shutdown_callback(close_db_engine)

    try:
        await asyncio.gather(
            start_bot(),
            start_web_server(),
        )
    except (KeyboardInterrupt, SystemExit):
        logger.info("Termination requested by user/system.")
    except Exception as e:
        logger.critical("Unexpected error during joint execution: %s", e)
    finally:
        await graceful_shutdown("FINAL_CLEANUP")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass