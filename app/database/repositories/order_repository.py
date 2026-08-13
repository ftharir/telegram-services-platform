from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OrderStatus
from app.database.models.order import Order


class OrderRepository:
    """مدیریت مستقیم کوئری‌های دیتابیس مربوط به سفارش‌ها."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """دریافت سفارش با ID داخلی."""
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tracking_code(self, tracking_code: str) -> Optional[Order]:
        """دریافت سفارش با کد پیگیری داخلی."""
        result = await self.session.execute(
            select(Order).where(Order.tracking_code == tracking_code)
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Order]:
        """دریافت سفارش بر اساس کلید یکتایی (جلوگیری از سفارش تکراری)."""
        result = await self.session.execute(
            select(Order).where(Order.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def create_order(
        self,
        user_id: int,
        tracking_code: str,
        idempotency_key: str,
        service_id: int,
        quantity: int,
        cost_coins: int,
        status: OrderStatus = OrderStatus.PENDING,
    ) -> Order:
        """ساخت یک سفارش جدید در حالت اولیه PENDING."""
        order = Order(
            user_id=user_id,
            tracking_code=tracking_code,
            idempotency_key=idempotency_key,
            service_id=service_id,
            quantity=quantity,
            cost_coins=cost_coins,
            status=status,
        )
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_user_orders(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> List[Order]:
        """دریافت سفارش‌های اخیر یک کاربر."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_open_orders(self) -> List[Order]:
        """دریافت تمام سفارش‌های باز جهت پیگیری وضعیت دوره‌ای از API."""
        open_statuses = [OrderStatus.SUBMITTED, OrderStatus.IN_PROGRESS]
        query = select(Order).where(Order.status.in_(open_statuses))
        result = await self.session.execute(query)
        return list(result.scalars().all())