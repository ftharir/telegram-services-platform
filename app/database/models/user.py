from datetime import datetime  # برای کار با تایپ تاریخ
from typing import Optional  # برای ستون‌هایی که می‌توانند مقدار خالی (Null/None) داشته باشند
from sqlalchemy import BigInteger, Boolean, String, DateTime, func  # تایپ‌های ستون PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column  # متد تعریف ستون در SQLAlchemy 2.0
from app.database.base import Base, TimestampMixin  # وارد کردن کلاس پایه و Mixin تاریخ
from app.core.constants import DEFAULT_LANGUAGE, Language  # کد زبان‌های پیش‌فرض پروژه


class User(Base, TimestampMixin):
    """مدل دیتابیس جدول کاربران (users)."""

    # نام جدول در دیتابیس PostgreSQL
    __tablename__ = "users"

    # ۱. شناسه داخلی دیتابیس (Primary Key) - عدد صحیح اتوماتیک (1, 2, 3, ...)
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ۲. شناسه عددی تلگرام (Telegram ID) - باید یکتا (Unique) و دارای Index برای جستجوی فوق‌العاده سریع باشد
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    # ۳. آیدی تلگرام کاربر (Username) - اختیاری است چون همه کاربران آیدی تلگرام ندارند
    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    # ۴. نام کاربر در تلگرام (First Name)
    first_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    # ۵. نام خانوادگی کاربر در تلگرام (Last Name) - اختیاری
    last_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    # ۶. کد زبان انتخابی کاربر ('fa' یا 'en') - پیش‌فرض fa (فارسی)
    language_code: Mapped[str] = mapped_column(
        String(10),
        default=DEFAULT_LANGUAGE.value,
        nullable=False,
    )

    # ۷. وضعیت فعال/غیرفعال بودن کاربر - پیش‌فرض True (فعال)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ۸. تاریخ آخرین فعالیت کاربر در ربات
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """یک نمایش متنی تمیز از مدل برای دیباگ و لاگ‌ها."""
        return (
            f"<User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username='{self.username}', lang='{self.language_code}')>"
        )