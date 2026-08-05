'''
import sys
from pathlib import Path

# اضافه کردن مسیر اصلی پروژه
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.bot.handlers import get_handlers_router
from app.bot.middlewares import DbSessionMiddleware
# from app.bot.middlewares.channel_checker import ForcedMemberMiddleware  # <--- ۱. اضافه شدن میدل‌ور عضویت اجباری
from app.core.config import settings
from app.core.logging import get_logger
from app.redis_client.client import close_redis, init_redis

logger = get_logger(__name__)


async def main() -> None:
    logger.info("Initializing Redis connection...")
    await init_redis()

    # تنظیم پروکسی محلی VPN
    session = AiohttpSession(proxy="socks5://127.0.0.1:10808")
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )

    dp = Dispatcher()

    # ۲. ثبت میدل‌ور دیتابیس (تزریق session و db_user)
    dp.update.outer_middleware(DbSessionMiddleware())

    # ۳. ثبت میدل‌ور عضویت اجباری کانال (بعد از میدل‌ور دیتابیس اجرا می‌شود)
    # dp.update.middleware(ForcedMemberMiddleware())

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
        logger.info("Bot stopped successfully.") '''


import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.bot.handlers import get_handlers_router
from app.bot.middlewares import DbSessionMiddleware
from app.bot.middlewares.channel_checker import ForcedMemberMiddleware
from app.core.config import settings
from app.core.logging import get_logger
from app.redis_client.client import close_redis, init_redis

logger = get_logger(__name__)


async def main() -> None:
    logger.info("Initializing Redis connection...")
    await init_redis()

    session = AiohttpSession(proxy="socks5://127.0.0.1:10808")
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )

    dp = Dispatcher()

    # ۱. ثبت میدل‌ور دیتابیس به صورت Outer
    dp.update.outer_middleware(DbSessionMiddleware())

    # دریافت روتر اصلی
    main_router = get_handlers_router()

    # ۲. ثبت میدل‌ور عضویت اجباری روی روتر اصلی (Inner Middleware)
    main_router.message.middleware(ForcedMemberMiddleware())
    main_router.callback_query.middleware(ForcedMemberMiddleware())

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