import asyncio
import uvicorn

from app.core.config import settings
from app.core.logging import get_logger
from app.main import main as start_bot
from app.web import app as fastapi_app

logger = get_logger(__name__)


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
    """اجرای همزمان و موازی ربات تلگرام و وب‌سرور FastAPI."""
    logger.info("Starting Telegram Services Platform (Bot + Web API)...")
    try:
        await asyncio.gather(
            start_bot(),
            start_web_server(),
        )
    except Exception as e:
        logger.critical("Error during joint execution of bot and web server: %s", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Platform stopped gracefully.")