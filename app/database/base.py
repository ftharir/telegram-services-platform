from datetime import datetime  # برای کار با تاریخ و زمان
from sqlalchemy import DateTime, func  # ابزارهای تعریف تایپ تاریخ و توابع دیتابیس در SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # ابزارهای مدرن SQLAlchemy 2.0


class Base(DeclarativeBase):
    """کلاس پایه (Mother Class) برای تمامی مدل‌های دیتابیس SQLAlchemy.
    
    تمام مدل‌ها (مثل User) از این کلاس ارث‌بری می‌کنند تا SQLAlchemy بفهمد
    این‌ها مدل دیتابیس هستند.
    """
    pass


class TimestampMixin:
    """یک کلاس کمکی (Mixin) برای اضافه کردن خودکار ستون‌های تاریخ ساخت و به‌روزرسانی.
    
    با اضافه کردن این Mixin به هر مدلی، دو ستون created_at و updated_at
    به‌طور خودکار به آن جدول اضافه می‌شوند.
    """
    
    # ستون تاریخ و زمان ساخت رکوردی که به‌طور خودکار هنگام INSERT مقدار زمان فعلی سرور دیتابیس را می‌گیرد
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ستون تاریخ و زمان آخرین ویرایش که هنگام UPDATE به‌طور خودکار بروزرسانی می‌شود
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )