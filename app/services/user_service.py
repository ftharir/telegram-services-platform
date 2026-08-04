import logging  
from typing import Optional  

from sqlalchemy.ext.asyncio import AsyncSession  

from app.database.models.user import User  
from app.database.repositories.user_repository import UserRepository  

logger = logging.getLogger(__name__)


class UserService:
    """لایه سرویس برای مدیریت منطق تجاری کاربران و تراکنش‌های دیتابیس."""

    def __init__(self, session: AsyncSession) -> None:
        """مقداردهی اولیه UserService با دریافت Session دیتابیس و تعریف Repository."""
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """دریافت اطلاعات کاربر با شناسه تلگرام."""
        return await self.user_repo.get_by_telegram_id(telegram_id)

    async def register_or_update_user(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "fa",
    ) -> tuple[User, bool]:
        """ثبت‌نام کاربر جدید یا بروزرسانی زمان آخرین فعالیت و commit تراکنش.
        
        خروجی: تاپل شامل (شیء کاربر, آیا تازه ساخته شده است؟)
        """
        user, created = await self.user_repo.get_or_create(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            last_name=last_name,
            language_code=language_code,
        )

        
        if not created:
            await self.user_repo.update_last_activity(telegram_id)

        
        await self.session.commit()

        if created:
            logger.info("New user registered in database: telegram_id=%s", telegram_id)
        
        return user, created

    async def change_user_language(self, telegram_id: int, language_code: str) -> Optional[User]:
        """تغییر زبان کاربر و ثبت آن در دیتابیس."""
        user = await self.user_repo.update_language(telegram_id, language_code)
        if user:
            await self.session.commit()
            logger.info("User language updated: telegram_id=%s, lang=%s", telegram_id, language_code)
        return user