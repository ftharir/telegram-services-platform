from datetime import datetime  
from typing import Optional  
from sqlalchemy import BigInteger, Boolean, String, DateTime, func  
from sqlalchemy.orm import Mapped, mapped_column  
from app.database.base import Base, TimestampMixin  
from app.core.constants import DEFAULT_LANGUAGE, Language  


class User(Base, TimestampMixin):
    """مدل دیتابیس جدول کاربران (users)."""

    
    __tablename__ = "users"

    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    
    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    
    first_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    
    language_code: Mapped[str] = mapped_column(
        String(10),
        default=DEFAULT_LANGUAGE.value,
        nullable=False,
    )

    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    
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