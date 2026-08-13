import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OrderStatus
from app.core.logging import get_logger
from app.database.models.order import Order
from app.database.repositories.order_repository import OrderRepository

logger = get_logger(__name__)


class DuplicateOrderError(Exception):
    """خطای ثبت سفارش تکراری با کلید یکتای مشابه."""
    pass


class OrderService:
    """سرویس مدیریت هسته سفارش‌ها و کد پیگیری."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OrderRepository(session)

    @staticmethod
    def generate_tracking_code() -> str:
        """تولید کد پیگیری منحصر به‌فرد به فرمت: ORD-YYYYMMDD-XXXX."""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
        return f"ORD-{date_str}-{random_suffix}"

    async def create_internal_order(
        self,
        user_id: int,
        idempotency_key: str,
        service_id: int,
        quantity: int,
        cost_coins: int,
    ) -> Order:
        """ایجاد سفارش داخلی پایه با برسی کلید Idempotency."""
        existing_order = await self.repo.get_by_idempotency_key(idempotency_key)
        if existing_order:
            logger.warning(
                "Duplicate order attempt blocked. idempotency_key=%s", idempotency_key
            )
            raise DuplicateOrderError(
                f"An order with key '{idempotency_key}' already exists."
            )

        tracking_code = self.generate_tracking_code()
        order = await self.repo.create_order(
            user_id=user_id,
            tracking_code=tracking_code,
            idempotency_key=idempotency_key,
            service_id=service_id,
            quantity=quantity,
            cost_coins=cost_coins,
            status=OrderStatus.PENDING,
        )
        logger.info(
            "Internal order created: id=%s, tracking_code=%s, cost=%s",
            order.id, tracking_code, cost_coins
        )
        return order

    async def update_order_status(
        self,
        order: Order,
        new_status: OrderStatus,
        rapidseen_order_id: Optional[str] = None,
        remains: Optional[int] = None,
    ) -> Order:
        """به‌روزرسانی وضعیت و اطلاعات سفارش."""
        order.status = new_status
        if rapidseen_order_id:
            order.rapidseen_order_id = rapidseen_order_id
        if remains is not None:
            order.remains = remains

        await self.session.flush()
        logger.info(
            "Order status updated: order_id=%s, new_status=%s",
            order.id, new_status.value
        )
        return order