from decimal import Decimal, ROUND_HALF_UP
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.order_repository import OrderRepository
from app.services.wallet_service import WalletService
from app.integrations.rapidseen.client import RapidSeenClient
from app.core.enums import TransactionType
from app.database.models.order import Order, OrderStatus

logger = logging.getLogger(__name__)

MAPPING_STATUS = {
    "Pending": OrderStatus.PENDING,
    "In progress": OrderStatus.IN_PROGRESS,
    "Processing": OrderStatus.IN_PROGRESS,
    "Done": OrderStatus.COMPLETED,
    "Completed": OrderStatus.COMPLETED,
    "Canceled": OrderStatus.CANCELED,
    "Partial": OrderStatus.PARTIAL,
}

class OrderLifecycleService:
    def __init__(self, session: AsyncSession, rapidseen_client: RapidSeenClient):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.wallet_service = WalletService(session)
        self.rapidseen_client = rapidseen_client

    @staticmethod
    def _provider_order_id(order: Order) -> Optional[int]:
        """شناسه سفارش در RapidSeen (ذخیره‌شده به‌صورت رشته) به‌صورت عدد، یا None."""
        try:
            return int(order.rapidseen_order_id) if order.rapidseen_order_id else None
        except (TypeError, ValueError):
            logger.warning("Order %s has a non-numeric provider id: %r", order.id, order.rapidseen_order_id)
            return None

    async def process_open_orders(self):
        """شناسایی و بروزرسانی وضعیت سفارش‌های باز"""
        open_orders = await self.order_repo.get_open_orders()
        for order in open_orders:
            provider_id = self._provider_order_id(order)
            if provider_id is None:
                continue

            res = await self.rapidseen_client.get_status(provider_id)
            if res.error or not res.status:
                continue

            new_status = MAPPING_STATUS.get(res.status)
            if new_status and new_status != order.status:
                order.status = new_status
                if res.remains is not None:
                    order.remains = res.remains
                if new_status in (OrderStatus.CANCELED, OrderStatus.PARTIAL):
                    await self._process_refund_if_eligible(order, res.remains)

        await self.session.commit()

    async def request_cancel(self, order_id: int) -> str:
        """
        # BUSINESS RULE CONFIRMED:
        # Sending cancel to RapidSeen does not automatically mark order as CANCELED.
        # Result status ('Sent', 'Already sent', 'Not possible') is returned, and order
        # status will be updated via subsequent polling.
        """
        order = await self.order_repo.get_by_id(order_id)
        provider_id = self._provider_order_id(order) if order else None
        if provider_id is None:
            return "Not possible"

        res = await self.rapidseen_client.cancel_order(provider_id)
        return res.cancel or res.error or "Not possible"

    async def _process_refund_if_eligible(self, order: Order, remains: Optional[int]):
        """
        محاسبه و انجام Refund به صورت Idempotent و Atomic.
        """
        if order.refunded_coins:
            # already refunded once: never refund the same order twice
            return

        if remains is None or remains < 0 or order.quantity <= 0:
            # CONSERVATIVE FINANCIAL POLICY:
            # If remains is missing or invalid, do not perform automatic refund.
            logger.warning(f"Cannot calculate refund for order {order.id}: missing or invalid remains ({remains}).")
            return

        # FALLBACK POLICY:
        # No explicit coin rounding rule was found in the available client
        # requirements or RapidSeen documentation.
        # ROUND_HALF_UP is used as a predictable default for integer coins.
        # See docs/phase2-decisions.md.
        cost_dec = Decimal(str(order.cost_coins))
        remains_dec = Decimal(str(remains))
        qty_dec = Decimal(str(order.quantity))

        refund_dec = (cost_dec * remains_dec) / qty_dec
        refund_coins = int(refund_dec.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

        # کلمپ کردن مقدار refund بین 0 و cost_coins
        refund_coins = max(0, min(refund_coins, order.cost_coins))

        if refund_coins > 0:
            await self.wallet_service.credit(
                user_id=order.user_id,
                amount=refund_coins,
                transaction_type=TransactionType.REFUND,
                description=f"Refund for order #{order.tracking_code} ({order.status.value})",
            )
            order.refunded_coins = refund_coins
            logger.info(f"Refunded {refund_coins} coins to user {order.user_id} for order {order.id}")
