import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.bot.handlers.view_handler import router as view_router
from app.bot.handlers.view_multiple_handler import router as view_multi_router
from app.bot.handlers.order_tracking_handler import router as tracking_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher()
    
    dp.include_router(view_router)
    dp.include_router(view_multi_router)
    dp.include_router(tracking_router)
    
    print("🤖 Bot setup completed with Phase 3 routers!")

if __name__ == "__main__":
    asyncio.run(main())
