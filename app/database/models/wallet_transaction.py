from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TransactionType
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.wallet import Wallet


class WalletTransaction(Base, TimestampMixin):
    """مدل دیتابیس جدول تاریخچه تراکنش‌ها (wallet_transactions)."""

    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    wallet_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="مقدار سکه (برای افزایش مثبت، برای کاهش منفی)",
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, name="transaction_type_enum"),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # ارتباط با کیف پول
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<WalletTransaction(id={self.id}, wallet_id={self.wallet_id}, "
            f"amount={self.amount}, type='{self.transaction_type.value}')>"
        )