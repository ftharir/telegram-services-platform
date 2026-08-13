from datetime import datetime  
from sqlalchemy import DateTime, func  
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  


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
    
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    