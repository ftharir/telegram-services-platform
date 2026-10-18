import asyncio
from unittest.mock import AsyncMock
from app.database.models.order import Order, OrderStatus
from app.services.order_lifecycle_service import OrderLifecycleService
from app.integrations.rapidseen.schemas import RapidSeenOrderStatusResponse, RapidSeenCancelOrderResponse

async def test():
    # ۱. ساخت یک سفارش نمونه در حافظه بدون پاس دادن فیلدهای نامشخص
    mock_order = Order()
    mock_order.id = 101
    mock_order.user_id = 1
    mock_order.service_id = 1
    mock_order.quantity = 1000
    mock_order.cost_coins = 50
    mock_order.tracking_code = "ORD-TEST-TASK6"
    mock_order.rapidseen_order_id = "554433"
    mock_order.status = OrderStatus.IN_PROGRESS
    mock_order.idempotency_key = "task6_key_1"

    # ۲. موک کردن Session و Repositoryها
    mock_session = AsyncMock()
    
    # ۳. موک کردن RapidSeenClient
    mock_client = AsyncMock()
    mock_client.get_status.return_value = RapidSeenOrderStatusResponse(
        status="Done",
        remains=0
    )
    mock_client.cancel_order.return_value = RapidSeenCancelOrderResponse(cancel="Sent")

    # ۴. ساخت سرویس و جایگزینی OrderRepository با موک
    lifecycle_service = OrderLifecycleService(mock_session, rapidseen_client=mock_client)
    lifecycle_service.order_repo = AsyncMock()
    lifecycle_service.order_repo.get_open_orders.return_value = [mock_order]
    lifecycle_service.order_repo.get_by_id.return_value = mock_order

    # ۵. بررسی بروزرسانی وضعیت سفارش به COMPLETED
    await lifecycle_service.process_open_orders()
    assert mock_order.status == OrderStatus.COMPLETED
    print("1. Status Update Test PASSED! New status:", mock_order.status.value)

    # ۶. بررسی متد درخواست لغو
    cancel_res = await lifecycle_service.request_cancel(mock_order.id)
    assert cancel_res == "Sent"
    print("2. Cancel Request Test PASSED! Response:", cancel_res)

if __name__ == "__main__":
    asyncio.run(test())
