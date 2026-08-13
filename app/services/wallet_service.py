from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionType
from app.core.logging import get_logger
from app.database.models.wallet import Wallet
from app.database.models.wallet_transaction import WalletTransaction
from app.database.repositories.wallet_repository import WalletRepository

logger = get_logger(__name__)


class InsufficientBalanceError(Exception):
    """خطای عدم داشتن موجودی کافی برای انجام تراکنش."""
    pass


class WalletService:
    """سرویس منطق تجاری مدیریت کیف پول و تراکنش‌ها."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = WalletRepository(session)

    async def get_or_create_wallet(self, user_id: int) -> Wallet:
        """دریافت کیف پول کاربر یا ساخت آن در صورت عدم وجود."""
        wallet = await self.repo.get_by_user_id(user_id)
        if not wallet:
            wallet = await self.repo.create_wallet(user_id)
            logger.info("Wallet created for user_id=%s", user_id)
        return wallet

    async def get_balance(self, user_id: int) -> int:
        """دریافت موجودی فعلی کاربر."""
        wallet = await self.get_or_create_wallet(user_id)
        return wallet.balance

    async def credit(
        self,
        user_id: int,
        amount: int,
        transaction_type: TransactionType = TransactionType.CREDIT,
        description: Optional[str] = None,
    ) -> Tuple[Wallet, WalletTransaction]:
        """افزایش موجودی سکه کاربر (به صورت Atomic)."""
        if amount <= 0:
            raise ValueError("Amount for credit must be positive.")

        wallet = await self.repo.get_by_user_id(user_id, for_update=True)
        if not wallet:
            wallet = await self.repo.create_wallet(user_id)

        wallet.balance += amount
        tx = await self.repo.add_transaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            description=description or f"Credited {amount} coins",
        )
        logger.info(
            "Wallet credited: user_id=%s, amount=+%s, new_balance=%s",
            user_id, amount, wallet.balance
        )
        return wallet, tx

    async def debit(
        self,
        user_id: int,
        amount: int,
        transaction_type: TransactionType = TransactionType.DEBIT,
        description: Optional[str] = None,
    ) -> Tuple[Wallet, WalletTransaction]:
        """کاهش موجودی سکه کاربر با بررسی عدم منفی شدن موجودی."""
        if amount <= 0:
            raise ValueError("Amount for debit must be positive.")

        wallet = await self.repo.get_by_user_id(user_id, for_update=True)
        if not wallet or wallet.balance < amount:
            current_bal = wallet.balance if wallet else 0
            raise InsufficientBalanceError(
                f"Insufficient balance. Required: {amount}, Available: {current_bal}"
            )

        wallet.balance -= amount
        tx = await self.repo.add_transaction(
            wallet_id=wallet.id,
            amount=-amount,
            transaction_type=transaction_type,
            description=description or f"Debited {amount} coins",
        )
        logger.info(
            "Wallet debited: user_id=%s, amount=-%s, new_balance=%s",
            user_id, amount, wallet.balance
        )
        return wallet, tx

    async def get_transaction_history(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> List[WalletTransaction]:
        """دریافت تاریخچه تراکنش‌های کاربر."""
        wallet = await self.get_or_create_wallet(user_id)
        return await self.repo.get_transactions(wallet.id, limit=limit, offset=offset)