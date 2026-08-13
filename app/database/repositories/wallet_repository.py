from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.wallet import Wallet
from app.database.models.wallet_transaction import WalletTransaction


class WalletRepository:
    """مدیریت مستقیم کوئری‌های دیتابیس مربوط به کیف پول و تراکنش‌ها."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: int, for_update: bool = False) -> Optional[Wallet]:
        """دریافت کیف پول کاربر با امکان قفل صریح در دیتابیس (SELECT FOR UPDATE)."""
        query = select(Wallet).where(Wallet.user_id == user_id)
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_wallet(self, user_id: int, initial_balance: int = 0) -> Wallet:
        """ایجاد کیف پول جدید برای کاربر."""
        wallet = Wallet(user_id=user_id, balance=initial_balance)
        self.session.add(wallet)
        await self.session.flush()
        return wallet

    async def add_transaction(
        self,
        wallet_id: int,
        amount: int,
        transaction_type: str,
        description: Optional[str] = None,
    ) -> WalletTransaction:
        """ثبت یک تراکنش مالی جدید."""
        tx = WalletTransaction(
            wallet_id=wallet_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def get_transactions(
        self, wallet_id: int, limit: int = 10, offset: int = 0
    ) -> List[WalletTransaction]:
        """دریافت لیست تاریخچه تراکنش‌های کیف پول."""
        query = (
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet_id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())