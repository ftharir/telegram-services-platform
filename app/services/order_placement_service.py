from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OrderStatus, TransactionType
from app.core.logging import get_logger
from app.database.models.order import Order
from app.database.repositories.order_repository import OrderRepository
from app.integrations.rapidseen.client import RapidSeenClient, RapidSeenAPIError
from app.services.order_service import DuplicateOrderError, OrderService
from app.services.wallet_service import InsufficientBalanceError, WalletService

logger = get_logger(__name__)


class OrderPlacementError(Exception):
    """خطای عمومی در جریان ایجاد سفارش."""
    pass


class OrderPlacementService:
    """ارکستریتور ایجاد امن سفارش، کسر سکه و ارتباط با API سرویس‌دهنده."""

    def __init__(
        self,
        session: AsyncSession,
        rapidseen_client: Optional[RapidSeenClient] = None,
    ) -> None:
        self.session = session
        self.wallet_service = WalletService(session)
        self.order_service = OrderService(session)
        self.order_repo = OrderRepository(session)
        self.rapidseen_client = rapidseen_client or RapidSeenClient()

    async def place_order(
        self,
        user_id: int,
        service_id: int,
        quantity: int,
        cost_coins: int,
        target_link: str,
        idempotency_key: str,
    ) -> Order:
        """
        اجرای امن جریان سفارش:
        1. بررسی Idempotency جهت جلوگیری از ثبت تکراری
        2. بررسی موجودی و کسر سکه
        3. ساخت سفارش داخلی (PENDING)
        4. ارسال به API و ثبت ID یا بازگشت وجه در صورت بروز خطا
        """
        # ۱. بررسی idempotency_key قبل از هرگونه عملیات مالی
        existing_order = await self.order_repo.get_by_idempotency_key(idempotency_key)
        if existing_order:
            logger.warning("Duplicate order blocked for idempotency_key=%s", idempotency_key)
            raise DuplicateOrderError(f"Order with key '{idempotency_key}' already exists.")

        # ۲. بررسی و کسر سکه از کیف پول کاربر (درون DB Transaction با قفل صریح)
        try:
            await self.wallet_service.debit(
                user_id=user_id,
                amount=cost_coins,
                transaction_type=TransactionType.DEBIT,
                description=f"Payment for service #{service_id} (Qty: {quantity})",
            )
        except InsufficientBalanceError as e:
            logger.warning("Insufficient balance for user_id=%s to place order.", user_id)
            raise e

        # ۳. ایجاد سفارش داخلی اولیه در وضعیت PENDING
        order = await self.order_service.create_internal_order(
            user_id=user_id,
            idempotency_key=idempotency_key,
            service_id=service_id,
            quantity=quantity,
            cost_coins=cost_coins,
            target_link=target_link,
        )

        # ۴. ارسال درخواست ثبت سفارش به RapidSeen API
        try:
            api_resp = await self.rapidseen_client.add_order(
                service_id=service_id,
                link=target_link,
                quantity=quantity,
            )

            # بررسی خطای منطقی ارسالی از سمت API
            if api_resp.error:
                logger.error("RapidSeen API error response: %s", api_resp.error)
                await self._refund_and_fail(order, f"API Error: {api_resp.error}")
                raise OrderPlacementError(f"Provider error: {api_resp.error}")

            if not api_resp.order:
                logger.error("RapidSeen API returned invalid response (missing order ID).")
                await self._refund_and_fail(order, "Invalid response from provider API")
                raise OrderPlacementError("Provider returned invalid order ID.")

            # ۵. ثبت موفق سفارش در API و بروزرسانی به وضعیت SUBMITTED
            rapidseen_order_id = str(api_resp.order)
            await self.order_service.update_order_status(
                order=order,
                new_status=OrderStatus.SUBMITTED,
                rapidseen_order_id=rapidseen_order_id,
            )
            logger.info(
                "Order placed successfully. Tracking Code: %s, RapidSeen Order ID: %s",
                order.tracking_code,
                rapidseen_order_id,
            )
            return order

        except RapidSeenAPIError as e:
            # مدیریت کامل Timeout, Network Error و HTTP Status Error
            logger.error("Network/Client error while sending order to RapidSeen: %s", str(e))
            await self._refund_and_fail(order, f"Network Error: {str(e)}")
            raise OrderPlacementError("Failed to communicate with provider API") from e

    async def _refund_and_fail(self, order: Order, reason: str) -> None:
        """تغییر وضعیت سفارش به FAILED و عودت کامل سکه‌ها به کیف پول کاربر."""
        await self.order_service.update_order_status(order, OrderStatus.FAILED)
        await self.wallet_service.credit(
            user_id=order.user_id,
            amount=order.cost_coins,
            transaction_type=TransactionType.REFUND,
            description=f"Auto refund for failed order {order.tracking_code} ({reason})",
        )
        logger.info(
            "Auto refund completed. Refunded %s coins to user_id=%s for order %s",
            order.cost_coins,
            order.user_id,
            order.tracking_code,
        )