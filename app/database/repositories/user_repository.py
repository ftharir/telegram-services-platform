from datetime import datetime, timezone  # برای ساخت زمان سیستم
from typing import Optional  # برای تایپ مقادیر اختیاری

from sqlalchemy import select, update  # توابع ساخت کوئری در SQLAlchemy 2.0
from sqlalchemy.ext.asyncio import AsyncSession  # تایپ Session غیرهمزمان

from app.database.models.user import User  # وارد کردن مدل User


class UserRepository:
    """لایه مدیریت کوئری‌ها و عملیات دیتابیس برای جدول کاربران (users)."""

    def __init__(self, session: AsyncSession) -> None:
        """مقداردهی اولیه Repository با دریافت Session فعال دیتابیس."""
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """جستجو و دریافت اطلاعات یک کاربر بر اساس شناسه عددی تلگرام."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "fa",
    ) -> User:
        """ساخت و ذخیره یک کاربر جدید در دیتابیس."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
        self.session.add(user)
        await self.session.flush()  # ثبت تغییرات در Session جهت دریافت شناسه تولید شده (id)
        await self.session.refresh(user)  # بروزرسانی شیء پایتونی با داده‌های واقعی دیتابیس
        return user

    async def get_or_create(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "fa",
    ) -> tuple[User, bool]:
        """دریافت کاربر موجود یا ساخت کاربر جدید در صورت عدم وجود.
        
        خروجی: تاپل شامل (شیء کاربر, تاگ bool که True یعنی تازه ساخته شد و False یعنی وجود داشت)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user is not None:
            return user, False

        new_user = await self.create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            last_name=last_name,
            language_code=language_code,
        )
        return new_user, True

    async def update_last_activity(self, telegram_id: int) -> None:
        """به‌روزرسانی ستون last_activity_at به زمان جاری جهت پیگیری کاربران فعال."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_activity_at=now)
        )
        await self.session.execute(stmt)

    async def update_language(self, telegram_id: int, language_code: str) -> Optional[User]:
        """تغییر زبان انتخابی کاربر."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language_code=language_code)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()