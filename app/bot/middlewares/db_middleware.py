import logging
from typing import Any, Awaitable, Callable, Dict  

from aiogram import BaseMiddleware  
from aiogram.types import TelegramObject, User as TelegramUser  

from app.database.session import async_session_maker  
from app.services.user_service import UserService  

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """میدل‌ور اختصاصی برای مدیریت Session دیتابیس و ثبت‌نام خودکار کاربران."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """این متد قبل از هر درخواست تلگرام اجرا می‌شود."""
        
        
        event_user: TelegramUser | None = data.get("event_from_user")

        
        async with async_session_maker() as session:
            
            user_service = UserService(session)
            data["session"] = session
            data["user_service"] = user_service

            
            if event_user and not event_user.is_bot:
                try:
                    db_user, _ = await user_service.register_or_update_user(
                        telegram_id=event_user.id,
                        first_name=event_user.first_name,
                        username=event_user.username,
                        last_name=event_user.last_name,
                        language_code=event_user.language_code or "fa",
                    )
                    
                    data["db_user"] = db_user
                except Exception as e:
                    logger.error("Error auto-registering user %s: %s", event_user.id, e)

            
            return await handler(event, data)