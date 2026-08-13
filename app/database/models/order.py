from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import OrderStatus
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class Order(Base, TimestampMixin):
    """مدل دیتابیس جدول سفارش‌ها (orders)."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tracking_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="کد پیگیری منحصر به‌فرد داخلی",
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="کلید جلوگیری از ثبت تکراری سفارش",
    )

    rapidseen_order_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        index=True,
        comment="شناسه سفارش در API خارجی (RapidSeen)",
    )

    service_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="شناسه سرویس انتخاب‌شده",
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="تعداد سفارش",
    )

    cost_coins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="هزینه پرداختی به سکه",
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status_enum"),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )

    remains: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="تعداد باقی‌مانده در صورت Partial شدن",
    )

    refunded_coins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="میزان سکه بازگشت داده شده به کاربر",
    )

    # ارتباط با کاربر
    user: Mapped["User"] = relationship("User", backref="orders")

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, tracking_code='{self.tracking_code}', "
            f"status='{self.status.value}', cost={self.cost_coins})>"
        )