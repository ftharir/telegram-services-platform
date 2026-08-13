from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.wallet_transaction import WalletTransaction


class Wallet(Base, TimestampMixin):
    """مدل دیتابیس جدول کیف پول (wallets)."""

    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    balance: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # روابط (Relationships)
    user: Mapped["User"] = relationship("User", backref="wallet", uselist=False)
    transactions: Mapped[List["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # تضمین سطح دیتابیس برای جلوگیری از منفی شدن موجودی
        CheckConstraint("balance >= 0", name="check_wallet_balance_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Wallet(id={self.id}, user_id={self.user_id}, balance={self.balance})>"