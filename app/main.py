import sys
from pathlib import Path

# اضافه کردن مسیر اصلی پروژه
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession  # <--- ۱. ایمپورت سشن
from aiogram.enums import ParseMode

from app.bot.handlers import get_handlers_router
from app.bot.middlewares import DbSessionMiddleware
from app.core.config import settings
from app.core.logging import get_logger
from app.redis_client.client import close_redis, init_redis

logger = get_logger(__name__)


async def main() -> None:
    logger.info("Initializing Redis connection...")
    await init_redis()

    # ۲. تنظیم پروکسی محلی VPN (پورت 10809 برای v2rayN معمول است)
    session = AiohttpSession(proxy="socks5://127.0.0.1:10808")
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,  # <--- ۳. پاس دادن سشن به Bot
    )

    dp = Dispatcher()

    # ثبت میدل‌ور دیتابیس
    dp.update.outer_middleware(DbSessionMiddleware())

    # ثبت روترهای هندلر
    main_router = get_handlers_router()
    dp.include_router(main_router)

    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Closing Redis connection...")
        await close_redis()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped successfully.")